import type { ButtonHTMLAttributes, JSX, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  icon?: string
  children: ReactNode
}

const base =
  'inline-flex items-center justify-center gap-2 font-medium tracking-[0.01em] transition-all duration-150 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-50 disabled:pointer-events-none select-none'

const variants: Record<Variant, string> = {
  primary:
    'bg-accent text-surface-lowest hover:bg-accent-strong shadow-[0_1px_0_rgba(32,26,16,0.25)] active:translate-y-px',
  secondary:
    'bg-surface-lowest text-ink border border-line-strong/70 hover:border-accent hover:text-accent',
  ghost: 'text-ink-variant hover:text-ink underline-offset-4 hover:underline',
  danger: 'bg-error text-white hover:opacity-90',
}

const sizes: Record<Size, string> = {
  sm: 'h-8 px-3 text-[12.5px] rounded-sm',
  md: 'h-10 px-4 text-[13.5px] rounded',
  lg: 'h-11 px-5 text-[14px] rounded',
}

export function Button({
  variant = 'primary',
  size = 'md',
  icon,
  children,
  className = '',
  ...props
}: ButtonProps): JSX.Element {
  return (
    <button
      type="button"
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {icon && (
        <span
          aria-hidden="true"
          className="material-symbols-rounded text-[1.15em] leading-none"
        >
          {icon}
        </span>
      )}
      {children}
    </button>
  )
}
