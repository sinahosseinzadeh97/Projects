import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import cv2
import numpy as np
from tqdm import tqdm
from einops import rearrange
from timesformer_pytorch import TimeSformer
import glob
import json
import random

class SportVideoDataset(Dataset):
    """Dataset for sports videos for fine-tuning TimeSformer"""
    def __init__(self, 
                video_dir: str, 
                annotations_file: str = None, 
                num_frames: int = 8,
                image_size: int = 224,
                transform=None,
                split='train'):
        """
        Args:
            video_dir: Directory containing video files
            annotations_file: JSON file with video annotations
            num_frames: Number of frames to extract per video
            image_size: Size to resize frames to
            transform: Optional transforms to apply
            split: 'train', 'val', or 'test'
        """
        self.video_dir = video_dir
        self.num_frames = num_frames
        self.image_size = image_size
        self.transform = transform
        self.split = split
        
        # Exercise class labels
        self.classes = ["squat", "pushup", "lunge", "jumping_jack"]
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}
        
        # Load videos and annotations
        if annotations_file and os.path.exists(annotations_file):
            with open(annotations_file, 'r') as f:
                self.annotations = json.load(f)
            
            # Filter videos for current split
            self.videos = [v for v in self.annotations if v['split'] == split]
        else:
            # If no annotations file, just use all videos in directory
            self.videos = []
            for exercise_type in self.classes:
                exercise_dir = os.path.join(video_dir, exercise_type)
                if os.path.exists(exercise_dir):
                    video_files = glob.glob(os.path.join(exercise_dir, '*.mp4'))
                    for video_file in video_files:
                        self.videos.append({
                            'path': video_file,
                            'label': exercise_type,
                            'split': split
                        })
            
            # Shuffle videos and split
            random.shuffle(self.videos)
            if split == 'train':
                self.videos = self.videos[:int(len(self.videos) * 0.7)]
            elif split == 'val':
                self.videos = self.videos[int(len(self.videos) * 0.7):int(len(self.videos) * 0.85)]
            else:  # test
                self.videos = self.videos[int(len(self.videos) * 0.85):]
    
    def __len__(self):
        return len(self.videos)
    
    def __getitem__(self, idx):
        # Get video info
        video_info = self.videos[idx]
        video_path = video_info.get('path', os.path.join(self.video_dir, video_info.get('filename', '')))
        label = video_info.get('label', 'unknown')
        
        # Extract frames
        frames = self._extract_frames(video_path)
        
        # Convert label to index
        label_idx = self.class_to_idx.get(label, 0)
        
        return frames, label_idx
    
    def _extract_frames(self, video_path):
        """Extract frames from video"""
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame indices to extract (evenly distributed)
        frame_indices = np.linspace(0, total_frames - 1, self.num_frames, dtype=int)
        
        # Extract frames
        frames = []
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                # If can't read frame, create a blank one
                frame = np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)
            
            # Preprocess frame: resize and convert to RGB
            frame = cv2.resize(frame, (self.image_size, self.image_size))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Apply optional transform
            if self.transform:
                frame = self.transform(frame)
            else:
                # Normalize to [0, 1] and convert to torch tensor
                frame = frame / 255.0
                frame = torch.FloatTensor(frame).permute(2, 0, 1)  # (H, W, C) -> (C, H, W)
                
            frames.append(frame)
            
        cap.release()
        
        # Stack frames into single tensor
        frames_tensor = torch.stack(frames)  # (num_frames, 3, H, W)
        
        return frames_tensor


def train_model(model, train_loader, val_loader, device, args):
    """Train the TimeSformer model"""
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=2, verbose=True
    )
    
    # Training loop
    best_val_loss = float('inf')
    best_val_acc = 0.0
    
    for epoch in range(args.epochs):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        train_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{args.epochs} [Train]")
        for frames, labels in train_bar:
            # Move to device
            frames = frames.to(device)  # (batch, num_frames, 3, H, W)
            labels = labels.to(device)
            
            # Rearrange for TimeSformer
            frames = rearrange(frames, 'b f c h w -> b c f h w')
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(frames)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Calculate metrics
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            train_bar.set_postfix({
                'loss': train_loss / (train_bar.n + 1),
                'acc': 100. * train_correct / train_total
            })
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            val_bar = tqdm(val_loader, desc=f"Epoch {epoch+1}/{args.epochs} [Val]")
            for frames, labels in val_bar:
                # Move to device
                frames = frames.to(device)
                labels = labels.to(device)
                
                # Rearrange for TimeSformer
                frames = rearrange(frames, 'b f c h w -> b c f h w')
                
                # Forward pass
                outputs = model(frames)
                loss = criterion(outputs, labels)
                
                # Calculate metrics
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
                
                # Update progress bar
                val_bar.set_postfix({
                    'loss': val_loss / (val_bar.n + 1),
                    'acc': 100. * val_correct / val_total
                })
        
        # Calculate average metrics
        avg_train_loss = train_loss / len(train_loader)
        avg_train_acc = 100. * train_correct / train_total
        avg_val_loss = val_loss / len(val_loader)
        avg_val_acc = 100. * val_correct / val_total
        
        # Update learning rate
        scheduler.step(avg_val_loss)
        
        # Print epoch summary
        print(f"Epoch {epoch+1}/{args.epochs}:")
        print(f"  Train Loss: {avg_train_loss:.4f}, Train Acc: {avg_train_acc:.2f}%")
        print(f"  Val Loss: {avg_val_loss:.4f}, Val Acc: {avg_val_acc:.2f}%")
        
        # Save best model
        if avg_val_acc > best_val_acc:
            best_val_acc = avg_val_acc
            best_val_loss = avg_val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': avg_val_loss,
                'val_acc': avg_val_acc,
            }, os.path.join(args.output_dir, 'best_model.pth'))
            print(f"  Saved new best model with val_acc: {avg_val_acc:.2f}%")
        
        # Save checkpoint
        if (epoch + 1) % args.save_interval == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': avg_val_loss,
                'val_acc': avg_val_acc,
            }, os.path.join(args.output_dir, f'checkpoint_epoch{epoch+1}.pth'))
    
    print(f"Training completed. Best validation accuracy: {best_val_acc:.2f}%")


def main():
    parser = argparse.ArgumentParser(description="Fine-tune TimeSformer for Sports Video Analysis")
    parser.add_argument('--data_dir', type=str, required=True, help='Directory containing video data')
    parser.add_argument('--annotations', type=str, default=None, help='Path to annotations file')
    parser.add_argument('--output_dir', type=str, default='./models', help='Output directory for models')
    parser.add_argument('--num_frames', type=int, default=8, help='Number of frames to extract per video')
    parser.add_argument('--image_size', type=int, default=224, help='Size to resize frames to')
    parser.add_argument('--batch_size', type=int, default=4, help='Batch size for training')
    parser.add_argument('--learning_rate', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=1e-4, help='Weight decay')
    parser.add_argument('--epochs', type=int, default=20, help='Number of epochs to train')
    parser.add_argument('--save_interval', type=int, default=5, help='Save checkpoint every N epochs')
    parser.add_argument('--gpus', type=str, default='0', help='GPUs to use (comma-separated)')
    args = parser.parse_args()
    
    # Set up output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Set device
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpus
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create datasets
    train_dataset = SportVideoDataset(
        video_dir=args.data_dir,
        annotations_file=args.annotations,
        num_frames=args.num_frames,
        image_size=args.image_size,
        split='train'
    )
    
    val_dataset = SportVideoDataset(
        video_dir=args.data_dir,
        annotations_file=args.annotations,
        num_frames=args.num_frames,
        image_size=args.image_size,
        split='val'
    )
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    # Create model
    model = TimeSformer(
        dim=512,
        image_size=args.image_size,
        patch_size=16,
        num_frames=args.num_frames,
        num_classes=len(train_dataset.classes),
        depth=12,
        heads=8
    ).to(device)
    
    # Print model summary
    print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    print(f"Training with {len(train_dataset)} videos, validating with {len(val_dataset)} videos")
    
    # Train model
    train_model(model, train_loader, val_loader, device, args)


if __name__ == "__main__":
    main() 