import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { Search, X } from "lucide-react";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const filterSchema = z.object({
  searchTerm: z.string().optional(),
  subject: z.string().optional(),
  priceRange: z.object({
    min: z.string().optional(),
    max: z.string().optional(),
  }),
  availability: z.array(z.string()).optional(),
});

type FilterValues = z.infer<typeof filterSchema>;

type TutorFiltersProps = {
  onFilter: (filters: FilterValues) => void;
  onReset: () => void;
  initialValues: FilterValues;
};

export default function TutorFilters({ onFilter, onReset, initialValues }: TutorFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const form = useForm<FilterValues>({
    resolver: zodResolver(filterSchema),
    defaultValues: initialValues || {
      searchTerm: "",
      subject: "",
      priceRange: { min: "", max: "" },
      availability: [],
    },
  });

  const handleSubmit = (values: FilterValues) => {
    onFilter(values);
  };

  const handleReset = () => {
    form.reset({
      searchTerm: "",
      subject: "",
      priceRange: { min: "", max: "" },
      availability: [],
    });
    onReset();
  };

  const availabilityOptions = [
    { id: "weekdays", label: "Weekdays" },
    { id: "weekends", label: "Weekends" },
    { id: "evenings", label: "Evenings" },
  ];

  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-xl font-semibold">Filters</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {/* Search box */}
            <FormField
              control={form.control}
              name="searchTerm"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-medium">Search</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search by name or subject"
                        className="pl-10"
                        {...field}
                      />
                      {field.value && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-1 top-1.5 h-7 w-7 p-0"
                          onClick={() => {
                            field.onChange("");
                          }}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </FormControl>
                </FormItem>
              )}
            />

            {/* Subject filter */}
            <FormField
              control={form.control}
              name="subject"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-medium">Subject</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value || "all"}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="All Subjects" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="all">All Subjects</SelectItem>
                      <SelectItem value="mathematics">Mathematics</SelectItem>
                      <SelectItem value="physics">Physics</SelectItem>
                      <SelectItem value="chemistry">Chemistry</SelectItem>
                      <SelectItem value="biology">Biology</SelectItem>
                      <SelectItem value="computer-science">Computer Science</SelectItem>
                      <SelectItem value="english">English</SelectItem>
                      <SelectItem value="history">History</SelectItem>
                      <SelectItem value="languages">Languages</SelectItem>
                    </SelectContent>
                  </Select>
                </FormItem>
              )}
            />

            {/* Mobile view toggle for additional filters */}
            <div className="md:hidden">
              <Button
                type="button"
                variant="outline"
                className="w-full"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? "Hide Additional Filters" : "Show Additional Filters"}
              </Button>
            </div>

            {/* Additional filters (always visible on desktop, toggleable on mobile) */}
            <div className={`space-y-6 ${isExpanded ? "block" : "hidden md:block"}`}>
              {/* Price range */}
              <div>
                <FormLabel className="text-sm font-medium">Price Range</FormLabel>
                <div className="flex items-center space-x-4 mt-2">
                  <FormField
                    control={form.control}
                    name="priceRange.min"
                    render={({ field }) => (
                      <FormItem className="flex-1">
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="Min"
                            min="0"
                            {...field}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                  <span className="text-muted-foreground">to</span>
                  <FormField
                    control={form.control}
                    name="priceRange.max"
                    render={({ field }) => (
                      <FormItem className="flex-1">
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="Max"
                            min="0"
                            {...field}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>
              </div>

              {/* Availability */}
              <div>
                <FormLabel className="text-sm font-medium mb-2 block">Availability</FormLabel>
                <div className="space-y-2">
                  {availabilityOptions.map((option) => (
                    <FormField
                      key={option.id}
                      control={form.control}
                      name="availability"
                      render={({ field }) => {
                        return (
                          <FormItem
                            key={option.id}
                            className="flex flex-row items-start space-x-3 space-y-0"
                          >
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(option.id)}
                                onCheckedChange={(checked) => {
                                  return checked
                                    ? field.onChange([...(field.value || []), option.id])
                                    : field.onChange(
                                        field.value?.filter(
                                          (value) => value !== option.id
                                        ) || []
                                      );
                                }}
                              />
                            </FormControl>
                            <FormLabel className="text-sm font-normal cursor-pointer">
                              {option.label}
                            </FormLabel>
                          </FormItem>
                        );
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Apply/Reset buttons */}
            <div className="flex space-x-4">
              <Button type="submit" className="flex-grow">
                Apply Filters
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={handleReset}
              >
                Reset
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
