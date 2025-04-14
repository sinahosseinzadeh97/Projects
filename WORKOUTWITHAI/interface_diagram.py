import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Set background color
ax.set_facecolor('#f5f5f5')

# Remove axis ticks and labels
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Title
ax.set_title('Fitness App Backend API Interface', fontsize=18, pad=20)

# Create mobile app box
mobile_app = patches.Rectangle((0.1, 0.7), 0.2, 0.2, linewidth=2, edgecolor='#3498db', facecolor='#3498db', alpha=0.7)
ax.add_patch(mobile_app)
ax.text(0.2, 0.8, 'Mobile App', ha='center', va='center', color='white', fontsize=12, fontweight='bold')

# Create API server box
api_server = patches.Rectangle((0.4, 0.4), 0.2, 0.5, linewidth=2, edgecolor='#2ecc71', facecolor='#2ecc71', alpha=0.7)
ax.add_patch(api_server)
ax.text(0.5, 0.65, 'API Server', ha='center', va='center', color='white', fontsize=12, fontweight='bold')

# Create endpoints inside API server
endpoints = [
    'POST /token',
    'POST /users/',
    'GET /users/me/',
    'POST /workouts/',
    'GET /workouts/',
    'GET /workouts/{id}',
    'GET /users/me/stats'
]

for i, endpoint in enumerate(endpoints):
    y_pos = 0.6 - i * 0.05
    ax.text(0.5, y_pos, endpoint, ha='center', va='center', color='white', fontsize=8)

# Create database box
database = patches.Rectangle((0.7, 0.5), 0.2, 0.2, linewidth=2, edgecolor='#9b59b6', facecolor='#9b59b6', alpha=0.7)
ax.add_patch(database)
ax.text(0.8, 0.6, 'PostgreSQL\nDatabase', ha='center', va='center', color='white', fontsize=12, fontweight='bold')

# Create ML module box
ml_module = patches.Rectangle((0.4, 0.1), 0.2, 0.2, linewidth=2, edgecolor='#e74c3c', facecolor='#e74c3c', alpha=0.7)
ax.add_patch(ml_module)
ax.text(0.5, 0.2, 'ML Video\nAnalysis', ha='center', va='center', color='white', fontsize=12, fontweight='bold')

# Create worker box
worker = patches.Rectangle((0.7, 0.1), 0.2, 0.2, linewidth=2, edgecolor='#f39c12', facecolor='#f39c12', alpha=0.7)
ax.add_patch(worker)
ax.text(0.8, 0.2, 'Celery\nWorker', ha='center', va='center', color='white', fontsize=12, fontweight='bold')

# Create monitoring box
monitoring = patches.Rectangle((0.1, 0.1), 0.2, 0.2, linewidth=2, edgecolor='#34495e', facecolor='#34495e', alpha=0.7)
ax.add_patch(monitoring)
ax.text(0.2, 0.2, 'Prometheus\nGrafana', ha='center', va='center', color='white', fontsize=12, fontweight='bold')

# Add arrows
arrow_props = dict(arrowstyle='->', linewidth=2, color='#7f8c8d')

# Mobile app to API
ax.annotate('', xy=(0.4, 0.8), xytext=(0.3, 0.8), arrowprops=arrow_props)
ax.text(0.35, 0.83, 'HTTP Requests', ha='center', va='center', fontsize=8)

# API to Database
ax.annotate('', xy=(0.7, 0.6), xytext=(0.6, 0.6), arrowprops=arrow_props)
ax.text(0.65, 0.63, 'CRUD', ha='center', va='center', fontsize=8)

# API to Worker
ax.annotate('', xy=(0.7, 0.2), xytext=(0.6, 0.4), arrowprops=arrow_props)
ax.text(0.65, 0.35, 'Tasks', ha='center', va='center', fontsize=8)

# Worker to ML
ax.annotate('', xy=(0.6, 0.2), xytext=(0.7, 0.2), arrowprops=arrow_props)
ax.text(0.65, 0.23, 'Process', ha='center', va='center', fontsize=8)

# API to Monitoring
ax.annotate('', xy=(0.2, 0.3), xytext=(0.4, 0.4), arrowprops=arrow_props)
ax.text(0.3, 0.35, 'Metrics', ha='center', va='center', fontsize=8)

# Add legend for API documentation
doc_patch = patches.Rectangle((0.1, 0.4), 0.2, 0.2, linewidth=2, edgecolor='#1abc9c', facecolor='#1abc9c', alpha=0.7)
ax.add_patch(doc_patch)
ax.text(0.2, 0.5, 'API Docs\n/docs\n/redoc', ha='center', va='center', color='white', fontsize=10, fontweight='bold')

# Add arrow from API to Docs
ax.annotate('', xy=(0.3, 0.5), xytext=(0.4, 0.5), arrowprops=arrow_props)
ax.text(0.35, 0.53, 'Generates', ha='center', va='center', fontsize=8)

# Add note about authentication
ax.text(0.5, 0.95, 'Authentication: JWT Bearer Token', ha='center', va='center', fontsize=10, fontweight='bold', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor='#f1c40f', alpha=0.7))

# Save the figure
plt.tight_layout()
plt.savefig('api_interface_diagram.png', dpi=300, bbox_inches='tight')
print("Diagram saved as 'api_interface_diagram.png'")
