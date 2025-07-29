import { render, screen, cleanup } from "@testing-library/react";
import { InputContentArea } from "./InputContentArea.jsx";

afterEach(cleanup);

describe("InputContentArea Component", () => {
  it("renders with default props", () => {
    render(<InputContentArea />);
    const input = screen.getByRole("textbox");
    expect(input).toBeInTheDocument();
    expect(input).toHaveClass("input-content-area");
  });

  it("renders with custom className", () => {
    render(<InputContentArea className="custom-class" />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveClass("input-content-area custom-class");
  });

  it("renders with placeholder text", () => {
    render(<InputContentArea placeholder="Enter text here" />);
    const input = screen.getByPlaceholderText("Enter text here");
    expect(input).toBeInTheDocument();
  });

  it("renders with initial value", () => {
    render(<InputContentArea value="Initial Value" />);
    const input = screen.getByDisplayValue("Initial Value");
    expect(input).toBeInTheDocument();
  });

  it("should be required", () => {
    render(<InputContentArea required={true} />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveAttribute("required");
  });

  it("should render left icon", () => {
    const leftIcon = <span className="left-icon">Left</span>;
    render(<InputContentArea leftIcon={leftIcon} />);
    expect(screen.getByText("Left")).toBeInTheDocument();
  });

  it("should render right icon", () => {
    const rightIcon = <span className="right-icon">Right</span>;
    render(<InputContentArea rightIcon={rightIcon} />);
    expect(screen.getByText("Right")).toBeInTheDocument();
  });
});
