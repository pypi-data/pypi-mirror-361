import { render, cleanup } from "@testing-library/react";
import { Spinner } from "./Spinner.jsx";

afterEach(cleanup);

describe("Spinner Component", () => {
  it("renders with default props", () => {
    const { container } = render(<Spinner />);
    const spinner = container.querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
  });

  it("renders with custom className", () => {
    const { container } = render(<Spinner className="custom-class" />);
    const spinner = container.querySelector(".animate-spin");
    expect(spinner).toHaveClass("custom-class");
  });
});
