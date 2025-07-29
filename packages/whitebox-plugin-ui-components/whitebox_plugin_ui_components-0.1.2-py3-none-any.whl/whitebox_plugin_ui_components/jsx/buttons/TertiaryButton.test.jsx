import { render, screen, cleanup } from "@testing-library/react";
import { TertiaryButton } from "./TertiaryButton.jsx";

afterEach(cleanup);

describe("TertiaryButton Component", () => {
  it("renders with default props", () => {
    render(<TertiaryButton />);
    const button = screen.getByRole("button");
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("btn btn-tertiary");
  });

  it("renders with custom className", () => {
    render(<TertiaryButton className="custom-class" />);
    const button = screen.getByRole("button");
    expect(button).toHaveClass("btn btn-tertiary custom-class");
  });

  it("renders with text", () => {
    render(<TertiaryButton text="Click Me" />);
    const button = screen.getByRole("button");
    expect(button).toHaveTextContent("Click Me");
  });

  it("renders with left icon", () => {
    const leftIcon = <span className="left-icon">Left</span>;
    render(<TertiaryButton leftIcon={leftIcon} />);
    const button = screen.getByRole("button");
    expect(button).toContainElement(screen.getByText("Left"));
  });

  it("renders with right icon", () => {
    const rightIcon = <span className="right-icon">Right</span>;
    render(<TertiaryButton rightIcon={rightIcon} />);
    const button = screen.getByRole("button");
    expect(button).toContainElement(screen.getByText("Right"));
  });

  it("renders with loading state", () => {
    render(<TertiaryButton isLoading={true} />);

    const spinner = screen.getByRole("button").querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("block");
  });

  it("does not render spinner when not loading", () => {
    render(<TertiaryButton isLoading={false} />);
    const spinner = screen.queryByRole("button").querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("hidden");
  });
});
