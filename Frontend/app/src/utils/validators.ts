import { z } from 'zod';
import i18n from '../i18n';

const tv = (key: string) => i18n.t(key, { ns: 'validation' });

export const createEmailSchema = () => z.string().email(tv('invalidEmail'));

export const createPasswordSchema = () =>
  z
    .string()
    .min(8, tv('passwordMinLength'))
    .regex(/[A-Z]/, tv('passwordUppercase'))
    .regex(/[a-z]/, tv('passwordLowercase'))
    .regex(/[0-9]/, tv('passwordDigit'))
    .regex(/[^A-Za-z0-9]/, tv('passwordSpecialChar'));

export const createLoginSchema = () =>
  z.object({
    email: createEmailSchema(),
    password: z.string().min(1, tv('passwordRequired')),
  });

export const createRegisterSchema = () =>
  z
    .object({
      email: createEmailSchema(),
      password: createPasswordSchema(),
      confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: tv('passwordsDoNotMatch'),
      path: ['confirmPassword'],
    });

export const createForgotPasswordSchema = () =>
  z.object({
    email: createEmailSchema(),
  });

export const createResetPasswordSchema = () =>
  z
    .object({
      password: createPasswordSchema(),
      confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: tv('passwordsDoNotMatch'),
      path: ['confirmPassword'],
    });

export const createProductCreateSchema = () =>
  z.object({
    url: z.string().url(tv('invalidUrl')).min(1, tv('urlRequired')),
    target_price: z.number().positive(tv('targetPricePositive')).min(0.01, tv('targetPriceMin')),
    check_frequency: z.union([z.literal(6), z.literal(12), z.literal(24)]).default(24),
  });

export const createProductUpdateSchema = () =>
  z.object({
    name: z.string().min(1, tv('nameRequired')).optional(),
    target_price: z
      .number()
      .positive(tv('targetPricePositive'))
      .min(0.01, tv('targetPriceMin'))
      .optional(),
    check_frequency: z.union([z.literal(6), z.literal(12), z.literal(24)]).optional(),
  });

// Static schemas for backward compatibility (use factory functions in components for i18n)
export const emailSchema = createEmailSchema();
export const passwordSchema = createPasswordSchema();
export const loginSchema = createLoginSchema();
export const registerSchema = createRegisterSchema();
export const forgotPasswordSchema = createForgotPasswordSchema();
export const resetPasswordSchema = createResetPasswordSchema();
export const productCreateSchema = createProductCreateSchema();
export const productUpdateSchema = createProductUpdateSchema();

export type LoginFormData = z.infer<ReturnType<typeof createLoginSchema>>;
export type RegisterFormData = z.infer<ReturnType<typeof createRegisterSchema>>;
export type ForgotPasswordFormData = z.infer<ReturnType<typeof createForgotPasswordSchema>>;
export type ResetPasswordFormData = z.infer<ReturnType<typeof createResetPasswordSchema>>;
export type ProductCreateFormData = z.input<ReturnType<typeof createProductCreateSchema>>;
export type ProductUpdateFormData = z.infer<ReturnType<typeof createProductUpdateSchema>>;
