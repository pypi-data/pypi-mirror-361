import { render, screen, cleanup } from "@testing-library/react";
import { PrimaryButton } from "./PrimaryButton.jsx";

afterEach(cleanup);

describe("PrimaryButton Component", () => {
  it("renders with default props", () => {
    render(<PrimaryButton />);
    const button = screen.getByRole("button");
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("btn btn-primary");
  });

  it("renders with custom className", () => {
    render(<PrimaryButton className="custom-class" />);
    const button = screen.getByRole("button");
    expect(button).toHaveClass("btn btn-primary custom-class");
  });

  it("renders with text", () => {
    render(<PrimaryButton text="Click Me" />);
    const button = screen.getByRole("button");
    expect(button).toHaveTextContent("Click Me");
  });

  it("renders with left icon", () => {
    const leftIcon = <span className="left-icon">Left</span>;
    render(<PrimaryButton leftIcon={leftIcon} />);
    const button = screen.getByRole("button");
    expect(button).toContainElement(screen.getByText("Left"));
  });

  it("renders with right icon", () => {
    const rightIcon = <span className="right-icon">Right</span>;
    render(<PrimaryButton rightIcon={rightIcon} />);
    const button = screen.getByRole("button");
    expect(button).toContainElement(screen.getByText("Right"));
  });

  it("renders with loading state", () => {
    render(<PrimaryButton isLoading={true} />);

    const spinner = screen.getByRole("button").querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("block");
  });

  it("does not render spinner when not loading", () => {
    render(<PrimaryButton isLoading={false} />);
    const spinner = screen.queryByRole("button").querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("hidden");
  });
});
