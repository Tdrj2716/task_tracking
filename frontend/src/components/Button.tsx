import React from "react";

export interface ButtonProps {
  /**
   * ボタンのラベル
   */
  label: string;
  /**
   * ボタンのバリアント（スタイル）
   */
  variant?: "primary" | "secondary" | "danger";
  /**
   * ボタンのサイズ
   */
  size?: "small" | "medium" | "large";
  /**
   * ボタンが無効化されているかどうか
   */
  disabled?: boolean;
  /**
   * クリックイベントハンドラ
   */
  onClick?: () => void;
}

/**
 * 汎用的なボタンコンポーネント
 */
export const Button: React.FC<ButtonProps> = ({
  label,
  variant = "primary",
  size = "medium",
  disabled = false,
  onClick,
}) => {
  const baseClasses =
    "font-semibold rounded transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";

  const variantClasses = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 disabled:bg-blue-300",
    secondary: "bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500 disabled:bg-gray-300",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 disabled:bg-red-300",
  };

  const sizeClasses = {
    small: "px-3 py-1.5 text-sm",
    medium: "px-4 py-2 text-base",
    large: "px-6 py-3 text-lg",
  };

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`;

  return (
    <button type="button" className={classes} disabled={disabled} onClick={onClick}>
      {label}
    </button>
  );
};
