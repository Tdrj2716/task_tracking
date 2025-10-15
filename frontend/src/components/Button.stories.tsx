import type { Meta, StoryObj } from "@storybook/react-vite";

import { Button } from "./Button";

const meta = {
  title: "Components/Button",
  component: Button,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "danger"],
    },
    size: {
      control: "select",
      options: ["small", "medium", "large"],
    },
    disabled: {
      control: "boolean",
    },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * プライマリボタンのデフォルト表示
 */
export const Primary: Story = {
  args: {
    label: "Primary Button",
    variant: "primary",
    size: "medium",
  },
};

/**
 * セカンダリボタンの表示
 */
export const Secondary: Story = {
  args: {
    label: "Secondary Button",
    variant: "secondary",
    size: "medium",
  },
};

/**
 * 危険な操作用のボタン
 */
export const Danger: Story = {
  args: {
    label: "Delete",
    variant: "danger",
    size: "medium",
  },
};

/**
 * 小サイズのボタン
 */
export const Small: Story = {
  args: {
    label: "Small Button",
    variant: "primary",
    size: "small",
  },
};

/**
 * 大サイズのボタン
 */
export const Large: Story = {
  args: {
    label: "Large Button",
    variant: "primary",
    size: "large",
  },
};

/**
 * 無効化されたボタン
 */
export const Disabled: Story = {
  args: {
    label: "Disabled Button",
    variant: "primary",
    size: "medium",
    disabled: true,
  },
};
