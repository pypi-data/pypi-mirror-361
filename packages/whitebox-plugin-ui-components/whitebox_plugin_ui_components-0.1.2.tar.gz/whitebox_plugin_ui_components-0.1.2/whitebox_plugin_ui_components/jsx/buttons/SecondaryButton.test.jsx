import { render, screen, cleanup } from "@testing-library/react";
import { SecondaryButton } from "./SecondaryButton.jsx";

afterEach(cleanup);

describe("SecondaryButton Component", () => {
  it("renders with default props", () => {
    render(<SecondaryButton />);
    const button = screen.getByRole("button");
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("btn btn-secondary");
  });

  it("renders with custom className", () => {
    render(<SecondaryButton className="custom-class" />);
    const button = screen.getByRole("button");
    expect(button).toHaveClass("btn btn-secondary custom-class");
  });

  it("renders with text", () => {
    render(<SecondaryButton text="Click Me" />);
    const button = screen.getByRole("button");
    expect(button).toHaveTextContent("Click Me");
  });

  it("renders with left icon", () => {
    const leftIcon = <span className="left-icon">Left</span>;
    render(<SecondaryButton leftIcon={leftIcon} />);
    const button = screen.getByRole("button");
    expect(button).toContainElement(screen.getByText("Left"));
  });

  it("renders with right icon", () => {
    const rightIcon = <span className="right-icon">Right</span>;
    render(<SecondaryButton rightIcon={rightIcon} />);
    const button = screen.getByRole("button");
    expect(button).toContainElement(screen.getByText("Right"));
  });

  it("renders with loading state", () => {
    render(<SecondaryButton isLoading={true} />);

    const spinner = screen.getByRole("button").querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("block");
  });

  it("does not render spinner when not loading", () => {
    render(<SecondaryButton isLoading={false} />);
    const spinner = screen.queryByRole("button").querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("hidden");
  });
});
