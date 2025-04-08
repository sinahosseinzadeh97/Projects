import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

interface ProductFormProps {
  product?: any;
  onSuccess: () => void;
  onCancel: () => void;
}

// Form schema for product
const productSchema = z.object({
  name: z.string().min(2, 'Product name is required'),
  slug: z.string().min(2, 'Slug is required').regex(/^[a-z0-9-]+$/, 'Slug must be lowercase letters, numbers, and hyphens only'),
  description: z.string().optional(),
  price: z.coerce.number().min(0.01, 'Price must be greater than 0'),
  compareAtPrice: z.coerce.number().min(0).optional().nullable(),
  categoryId: z.coerce.number({
    required_error: "Category is required",
    invalid_type_error: "Category must be a number",
  }),
  imageUrl: z.string().optional(),
  stock: z.coerce.number().min(0, 'Stock cannot be negative'),
  isFeatured: z.boolean().default(false),
  isNew: z.boolean().default(false),
});

const ProductForm = ({ product, onSuccess, onCancel }: ProductFormProps) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch categories for the dropdown
  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['/api/categories'],
  });

  // Form setup
  const form = useForm({
    resolver: zodResolver(productSchema),
    defaultValues: {
      name: product?.name || '',
      slug: product?.slug || '',
      description: product?.description || '',
      price: product?.price || 0,
      compareAtPrice: product?.compareAtPrice || null,
      categoryId: product?.categoryId || '',
      imageUrl: product?.imageUrl || '',
      stock: product?.stock || 0,
      isFeatured: product?.isFeatured || false,
      isNew: product?.isNew || false,
    },
  });

  // Create product mutation
  const createProductMutation = useMutation({
    mutationFn: async (data) => {
      return apiRequest('POST', '/api/admin/products', data);
    },
    onSuccess: () => {
      toast({
        title: "Product created",
        description: "Product has been created successfully",
      });
      setIsSubmitting(false);
      onSuccess();
    },
    onError: (error: any) => {
      setIsSubmitting(false);
      toast({
        title: "Error creating product",
        description: error.message || "Something went wrong",
        variant: "destructive",
      });
    },
  });

  // Update product mutation
  const updateProductMutation = useMutation({
    mutationFn: async ({ id, data }) => {
      return apiRequest('PUT', `/api/admin/products/${id}`, data);
    },
    onSuccess: () => {
      toast({
        title: "Product updated",
        description: "Product has been updated successfully",
      });
      setIsSubmitting(false);
      onSuccess();
    },
    onError: (error: any) => {
      setIsSubmitting(false);
      toast({
        title: "Error updating product",
        description: error.message || "Something went wrong",
        variant: "destructive",
      });
    },
  });

  // Generate slug from name
  const generateSlug = (name: string) => {
    return name
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  // Handle form submission
  const onSubmit = (data) => {
    setIsSubmitting(true);
    
    // Convert empty strings to null/undefined
    if (data.compareAtPrice === 0 || data.compareAtPrice === '') {
      data.compareAtPrice = null;
    }
    
    if (product) {
      updateProductMutation.mutate({ id: product.id, data });
    } else {
      createProductMutation.mutate(data);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-6">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Product Name</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="e.g. Wireless Headphones" 
                      {...field} 
                      onChange={(e) => {
                        field.onChange(e);
                        // Auto-generate slug when name changes if slug is empty
                        const currentSlug = form.getValues('slug');
                        if (!currentSlug || (product && product.name === currentSlug)) {
                          form.setValue('slug', generateSlug(e.target.value));
                        }
                      }}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="slug"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Slug</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g. wireless-headphones" {...field} />
                  </FormControl>
                  <FormDescription>
                    Used in the URL, must be unique
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="categoryId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Category</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value?.toString()}
                    value={field.value?.toString()}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a category" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {!categories ? (
                        <SelectItem value="loading">Loading categories...</SelectItem>
                      ) : (
                        categories.map((category: any) => (
                          <SelectItem key={category.id} value={category.id.toString()}>
                            {category.name}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Price</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        placeholder="0.00"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="compareAtPrice"
                render={({ field: { value, onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>Compare at Price</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        placeholder="0.00"
                        value={value === null ? '' : value}
                        onChange={onChange}
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Original price, if on sale
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="stock"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Stock Quantity</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min="0"
                      placeholder="0"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="space-y-6">
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Enter product description"
                      className="h-32"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="imageUrl"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Image URL</FormLabel>
                  <FormControl>
                    <Input placeholder="https://example.com/image.jpg" {...field} />
                  </FormControl>
                  <FormDescription>
                    Link to the product image
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="pt-2">
              <div className="flex flex-col space-y-4">
                <FormField
                  control={form.control}
                  name="isFeatured"
                  render={({ field }) => (
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="isFeatured"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                      <Label htmlFor="isFeatured">Featured Product</Label>
                    </div>
                  )}
                />

                <FormField
                  control={form.control}
                  name="isNew"
                  render={({ field }) => (
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="isNew"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                      <Label htmlFor="isNew">New Arrival</Label>
                    </div>
                  )}
                />
              </div>
            </div>

            {field.value && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-500 mb-2">Product Preview</p>
                <div className="border border-gray-200 rounded-md p-4">
                  {field.value ? (
                    <img
                      src={field.value}
                      alt="Product preview"
                      className="w-full h-40 object-contain rounded-md"
                    />
                  ) : (
                    <div className="w-full h-40 bg-gray-100 rounded-md flex items-center justify-center text-gray-400">
                      <span>No image URL provided</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <Separator />

        <div className="flex justify-end space-x-2">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? 'Saving...'
              : product
                ? 'Update Product'
                : 'Create Product'}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default ProductForm;
