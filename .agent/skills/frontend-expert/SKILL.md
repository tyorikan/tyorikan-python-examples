---
name: frontend-expert 
description: React, TypeScript, and Tailwind CSS patterns. Includes component structure, TanStack Query integration, form handling with Zod, and UI best practices.
---

# Frontend Development Patterns (React)

Standards for building maintainable and responsive UIs.

## Component Patterns

### Feature-Based Folder Structure

Group files by feature rather than type.
```
src/
├── features/
│   ├── auth/
│   │   ├── components/  # Auth specific UI
│   │   ├── hooks/       # Auth logic
│   │   └── api/         # Auth API calls
│   └── dashboard/
├── components/
│   ├── ui/             # Generic (Buttons, Inputs)
│   └── layout/         # Header, Sidebar
├── lib/                # Utils (axios, queryClient)
└── hooks/              # Global hooks
```

### Typed Component Props

```typescript
import { ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

interface ButtonProps 
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  leftIcon?: ReactNode;
}

export const Button = ({ 
  className, 
  variant, 
  size, 
  isLoading, 
  leftIcon,
  children, 
  ...props 
}: ButtonProps) => {
  // Implementation...
};
```

## Data Fetching (TanStack Query)

### Custom Query Hook
```typescript
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { User } from '@/types';

export const useUsers = (filters?: UserFilters) => {
  return useQuery({
    queryKey: ['users', filters],
    queryFn: async () => {
      const { data } = await api.get<User[]>('/users', { params: filters });
      return data;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};
```

### Mutation Hook
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (newUser: CreateUserDto) => api.post('/users', newUser),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast({ title: "User created successfully" });
    },
    onError: (error) => {
      toast({ 
        title: "Error", 
        description: error.message, 
        variant: "destructive" 
      });
    },
  });
};
```

## Form Handling (React Hook Form + Zod)
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const formSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type FormValues = z.infer<typeof formSchema>;

export const LoginForm = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
  });

  const onSubmit = (data: FormValues) => {
    // Handle login
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Inputs with error display */}
    </form>
  );
};
```
