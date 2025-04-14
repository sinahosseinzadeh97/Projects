import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

// Form schema for Category
const categoryFormSchema = z.object({
  name: z.string().min(2, 'Category name is required'),
  slug: z.string().min(2, 'Slug is required').regex(/^[a-z0-9-]+$/, 'Slug must be lowercase letters, numbers, and hyphens only'),
  description: z.string().optional(),
  imageUrl: z.string().optional(),
});

// Form schema for Subscriber Export
const subscriberExportFormSchema = z.object({
  format: z.enum(['csv', 'json'], {
    required_error: "Please select a format",
  }),
});

const Content = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [activeTab, setActiveTab] = useState('categories');
  const [isAddCategoryOpen, setIsAddCategoryOpen] = useState(false);
  const [isEditCategoryOpen, setIsEditCategoryOpen] = useState(false);
  const [currentCategory, setCurrentCategory] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Fetch categories
  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['/api/categories'],
  });

  // Fetch newsletter subscribers
  const { data: subscribers, isLoading: subscribersLoading } = useQuery({
    queryKey: ['/api/admin/subscribers'],
    enabled: activeTab === 'newsletter',
  });

  // Category form
  const categoryForm = useForm({
    resolver: zodResolver(categoryFormSchema),
    defaultValues: {
      name: '',
      slug: '',
      description: '',
      imageUrl: '',
    },
  });

  // Export form
  const exportForm = useForm({
    resolver: zodResolver(subscriberExportFormSchema),
    defaultValues: {
      format: 'csv',
    },
  });

  // Create category mutation
  const createCategoryMutation = useMutation({
    mutationFn: async (data) => {
      return apiRequest('POST', '/api/admin/categories', data);
    },
    onSuccess: () => {
      toast({
        title: "Category created",
        description: "Category has been created successfully",
      });
      categoryForm.reset();
      setIsAddCategoryOpen(false);
      queryClient.invalidateQueries({ queryKey: ['/api/categories'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error creating category",
        description: error.message || "Something went wrong",
        variant: "destructive",
      });
    },
  });

  // Update category mutation
  const updateCategoryMutation = useMutation({
    mutationFn: async ({ id, data }) => {
      return apiRequest('PUT', `/api/admin/categories/${id}`, data);
    },
    onSuccess: () => {
      toast({
        title: "Category updated",
        description: "Category has been updated successfully",
      });
      categoryForm.reset();
      setIsEditCategoryOpen(false);
      setCurrentCategory(null);
      queryClient.invalidateQueries({ queryKey: ['/api/categories'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error updating category",
        description: error.message || "Something went wrong",
        variant: "destructive",
      });
    },
  });

  // Delete category mutation
  const deleteCategoryMutation = useMutation({
    mutationFn: async (id) => {
      return apiRequest('DELETE', `/api/admin/categories/${id}`);
    },
    onSuccess: () => {
      toast({
        title: "Category deleted",
        description: "Category has been deleted successfully",
      });
      setIsDeleteDialogOpen(false);
      setCategoryToDelete(null);
      setIsDeleting(false);
      queryClient.invalidateQueries({ queryKey: ['/api/categories'] });
    },
    onError: (error: any) => {
      setIsDeleting(false);
      toast({
        title: "Error deleting category",
        description: error.message || "Something went wrong",
        variant: "destructive",
      });
    },
  });

  // Handle category form submission
  const onCategorySubmit = (data) => {
    if (currentCategory) {
      updateCategoryMutation.mutate({ id: currentCategory.id, data });
    } else {
      createCategoryMutation.mutate(data);
    }
  };

  // Handle delete category
  const handleDeleteCategory = (category) => {
    setCategoryToDelete(category);
    setIsDeleteDialogOpen(true);
  };

  // Confirm delete category
  const confirmDeleteCategory = () => {
    if (categoryToDelete) {
      setIsDeleting(true);
      deleteCategoryMutation.mutate(categoryToDelete.id);
    }
  };

  // Handle edit category
  const handleEditCategory = (category) => {
    setCurrentCategory(category);
    categoryForm.reset({
      name: category.name,
      slug: category.slug,
      description: category.description || '',
      imageUrl: category.imageUrl || '',
    });
    setIsEditCategoryOpen(true);
  };

  // Handle export subscribers
  const onExportSubmit = (data) => {
    // This would typically trigger a download
    toast({
      title: "Export initiated",
      description: `Exporting ${subscribers?.length || 0} subscribers to ${data.format.toUpperCase()}`,
    });
    
    // In a real implementation, we would make an API call to generate the export
    // and then trigger a download
  };

  // Generate slug from name
  const generateSlug = (name: string) => {
    return name
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Content Management</h1>
      </div>

      <Tabs defaultValue="categories" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="newsletter">Newsletter</TabsTrigger>
        </TabsList>

        {/* Categories Tab */}
        <TabsContent value="categories">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Categories</CardTitle>
                  <CardDescription>Manage product categories</CardDescription>
                </div>
                <Button onClick={() => {
                  categoryForm.reset({
                    name: '',
                    slug: '',
                    description: '',
                    imageUrl: '',
                  });
                  setIsAddCategoryOpen(true);
                }}>
                  <i className="fas fa-plus mr-2"></i> Add Category
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {categoriesLoading ? (
                <div className="flex justify-center items-center h-48">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Image</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Slug</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {categories?.map(category => (
                        <TableRow key={category.id}>
                          <TableCell>
                            <div className="h-10 w-10 rounded bg-gray-100 overflow-hidden">
                              {category.imageUrl ? (
                                <img
                                  src={category.imageUrl}
                                  alt={category.name}
                                  className="h-full w-full object-cover"
                                />
                              ) : (
                                <div className="flex items-center justify-center h-full text-gray-400">
                                  <i className="fas fa-image"></i>
                                </div>
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="font-medium">{category.name}</TableCell>
                          <TableCell className="text-sm text-gray-500">{category.slug}</TableCell>
                          <TableCell className="max-w-xs truncate">
                            {category.description || <span className="text-gray-400 italic">No description</span>}
                          </TableCell>
                          <TableCell>
                            <div className="flex space-x-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleEditCategory(category)}
                              >
                                <i className="fas fa-edit text-blue-600"></i>
                              </Button>
                              
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteCategory(category)}
                              >
                                <i className="fas fa-trash text-red-600"></i>
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                      
                      {(!categories || categories.length === 0) && (
                        <TableRow>
                          <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                            No categories found
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Newsletter Tab */}
        <TabsContent value="newsletter">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Newsletter Subscribers</CardTitle>
                <CardDescription>Manage your newsletter subscribers</CardDescription>
              </CardHeader>
              <CardContent>
                {subscribersLoading ? (
                  <div className="flex justify-center items-center h-48">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Email</TableHead>
                          <TableHead>Subscribed On</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {subscribers?.map(subscriber => (
                          <TableRow key={subscriber.id}>
                            <TableCell className="font-medium">{subscriber.email}</TableCell>
                            <TableCell>
                              {new Date(subscriber.createdAt).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                              })}
                            </TableCell>
                          </TableRow>
                        ))}
                        
                        {(!subscribers || subscribers.length === 0) && (
                          <TableRow>
                            <TableCell colSpan={2} className="text-center py-8 text-gray-500">
                              No subscribers found
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="text-sm text-gray-500">
                  Total Subscribers: {subscribers?.length || 0}
                </div>
              </CardFooter>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Export Subscribers</CardTitle>
                <CardDescription>Download your subscriber list</CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...exportForm}>
                  <form onSubmit={exportForm.handleSubmit(onExportSubmit)} className="space-y-6">
                    <FormField
                      control={exportForm.control}
                      name="format"
                      render={({ field }) => (
                        <FormItem className="space-y-3">
                          <FormLabel>Export Format</FormLabel>
                          <FormControl>
                            <div className="flex flex-col space-y-2">
                              <label className="flex items-center space-x-2">
                                <input
                                  type="radio"
                                  value="csv"
                                  checked={field.value === 'csv'}
                                  onChange={() => field.onChange('csv')}
                                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                                />
                                <span>CSV</span>
                              </label>
                              <label className="flex items-center space-x-2">
                                <input
                                  type="radio"
                                  value="json"
                                  checked={field.value === 'json'}
                                  onChange={() => field.onChange('json')}
                                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                                />
                                <span>JSON</span>
                              </label>
                            </div>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <Button type="submit" className="w-full">
                      <i className="fas fa-download mr-2"></i> Export Subscribers
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Add Category Dialog */}
      <Dialog open={isAddCategoryOpen} onOpenChange={setIsAddCategoryOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Category</DialogTitle>
            <DialogDescription>
              Create a new product category
            </DialogDescription>
          </DialogHeader>
          
          <Form {...categoryForm}>
            <form onSubmit={categoryForm.handleSubmit(onCategorySubmit)} className="space-y-6">
              <FormField
                control={categoryForm.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category Name</FormLabel>
                    <FormControl>
                      <Input 
                        {...field} 
                        placeholder="e.g. Electronics"
                        onChange={(e) => {
                          field.onChange(e);
                          // Auto-generate slug when name changes if slug is empty
                          const currentSlug = categoryForm.getValues('slug');
                          if (!currentSlug) {
                            categoryForm.setValue('slug', generateSlug(e.target.value));
                          }
                        }}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={categoryForm.control}
                name="slug"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Slug</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="e.g. electronics" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={categoryForm.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description (Optional)</FormLabel>
                    <FormControl>
                      <Textarea {...field} placeholder="Enter category description" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={categoryForm.control}
                name="imageUrl"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Image URL (Optional)</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="https://example.com/image.jpg" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <DialogFooter>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setIsAddCategoryOpen(false)}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit"
                  disabled={createCategoryMutation.isPending}
                >
                  {createCategoryMutation.isPending ? "Creating..." : "Create Category"}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* Edit Category Dialog */}
      <Dialog open={isEditCategoryOpen} onOpenChange={setIsEditCategoryOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Category</DialogTitle>
            <DialogDescription>
              Update the category details
            </DialogDescription>
          </DialogHeader>
          
          <Form {...categoryForm}>
            <form onSubmit={categoryForm.handleSubmit(onCategorySubmit)} className="space-y-6">
              <FormField
                control={categoryForm.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category Name</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="e.g. Electronics" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={categoryForm.control}
                name="slug"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Slug</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="e.g. electronics" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={categoryForm.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description (Optional)</FormLabel>
                    <FormControl>
                      <Textarea {...field} placeholder="Enter category description" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={categoryForm.control}
                name="imageUrl"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Image URL (Optional)</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="https://example.com/image.jpg" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <DialogFooter>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setIsEditCategoryOpen(false);
                    setCurrentCategory(null);
                  }}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit"
                  disabled={updateCategoryMutation.isPending}
                >
                  {updateCategoryMutation.isPending ? "Updating..." : "Update Category"}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* Delete Category Confirmation */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the category
              <span className="font-bold"> {categoryToDelete?.name}</span> and may affect products
              associated with it.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel 
              onClick={() => {
                setIsDeleteDialogOpen(false);
                setCategoryToDelete(null);
              }}
            >
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction 
              onClick={confirmDeleteCategory}
              className="bg-red-600 hover:bg-red-700"
              disabled={isDeleting}
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Content;
