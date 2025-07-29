import Spinner from "../common/Spinner";

const { utils } = Whitebox;

const Button = ({
  typeClass,
  text = null,
  onClick = null,
  leftIcon = null,
  rightIcon = null,
  className = null,
  isLoading = false,
  ...props
}) => {
  let paddingClasses = "px-6 py-3";
  if ((leftIcon || rightIcon) && !text) {
    paddingClasses = "px-3 py-3";
  }

  const computedClassName = utils.getClasses(
    "btn",
    typeClass,
    className,
    paddingClasses
  );

  return (
    <button className={computedClassName} onClick={onClick} {...props}>
      <Spinner
        className={
          "absolute origin-center" + (isLoading ? " block" : " hidden")
        }
      />

      <div className={isLoading ? "invisible" : undefined}>
        {leftIcon && <div className="icon-container">{leftIcon}</div>}

        {text}

        {rightIcon && <div className="icon-container">{rightIcon}</div>}
      </div>
    </button>
  );
};

export { Button };
export default Button;
