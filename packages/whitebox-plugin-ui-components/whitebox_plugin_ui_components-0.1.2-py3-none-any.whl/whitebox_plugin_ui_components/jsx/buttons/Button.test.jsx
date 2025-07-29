import { render, screen, cleanup } from "@testing-library/react";
import { Button } from "./Button.jsx";

afterEach(cleanup);

describe("Button Component", () => {
  it("renders with default props", () => {
    render(<Button />);
    const button = screen.getByRole("button");
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("btn");
  });

  it("renders with custom className", () => {
    render(<Button className="custom-class" />);
    const button = screen.getByRole("button");
    expect(button).toHaveClass("btn custom-class");
  });

  it("renders with custom typeClass", () => {
    render(<Button typeClass="btn-secondary" />);
    const button = screen.getByRole("button");
    expect(button).toHaveClass("btn-secondary");
  });

  it("renders with text", () => {
    render(<Button text="Click Me" />);
    const button = screen.getByRole("button");
    expect(button).toHaveTextContent("Click Me");
  });

  it("renders with left icon", () => {
    const leftIcon = <span className="left-icon">Left</span>;
    render(<Button leftIcon={leftIcon} />);
    const button = screen.getByRole("button");
    expect(button).toContainElement(screen.getByText("Left"));
  });

  it("renders with right icon", () => {
    const rightIcon = <span className="right-icon">Right</span>;
    render(<Button rightIcon={rightIcon} />);
    const button = screen.getByRole("button");
    expect(button).toContainElement(screen.getByText("Right"));
  });

  it("renders with loading state", () => {
    render(<Button isLoading={true} />);

    const spinner = screen.getByRole("button").querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("block");
  });

  it("does not render spinner when not loading", () => {
    render(<Button isLoading={false} />);
    const spinner = screen.queryByRole("button").querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("hidden");
  });
});
