import { z } from 'zod';

export const emailSchema = z.string().email('Email invalide');

export const passwordSchema = z
  .string()
  .min(8, 'Le mot de passe doit contenir au moins 8 caractères')
  .regex(/[A-Z]/, 'Le mot de passe doit contenir au moins une majuscule')
  .regex(/[a-z]/, 'Le mot de passe doit contenir au moins une minuscule')
  .regex(/[0-9]/, 'Le mot de passe doit contenir au moins un chiffre')
  .regex(/[^A-Za-z0-9]/, 'Le mot de passe doit contenir au moins un caractère spécial');

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Le mot de passe est requis'),
});

export const registerSchema = z
  .object({
    email: emailSchema,
    password: passwordSchema,
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Les mots de passe ne correspondent pas',
    path: ['confirmPassword'],
  });

export const forgotPasswordSchema = z.object({
  email: emailSchema,
});

export const resetPasswordSchema = z
  .object({
    password: passwordSchema,
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Les mots de passe ne correspondent pas',
    path: ['confirmPassword'],
  });

const productCreateSchemaBase = z.object({
  url: z.string().url('URL invalide').min(1, "L'URL est requise"),
  target_price: z
    .number()
    .positive('Le prix cible doit être positif')
    .min(0.01, 'Le prix cible doit être au moins 0.01€'),
  check_frequency: z.union([z.literal(6), z.literal(12), z.literal(24)]).default(24),
});

export const productCreateSchema = productCreateSchemaBase;

export const productUpdateSchema = z.object({
  name: z.string().min(1, 'Le nom est requis').optional(),
  target_price: z
    .number()
    .positive('Le prix cible doit être positif')
    .min(0.01, 'Le prix cible doit être au moins 0.01€')
    .optional(),
  check_frequency: z.union([z.literal(6), z.literal(12), z.literal(24)]).optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
export type ProductCreateFormData = z.input<typeof productCreateSchema>;
export type ProductUpdateFormData = z.infer<typeof productUpdateSchema>;
