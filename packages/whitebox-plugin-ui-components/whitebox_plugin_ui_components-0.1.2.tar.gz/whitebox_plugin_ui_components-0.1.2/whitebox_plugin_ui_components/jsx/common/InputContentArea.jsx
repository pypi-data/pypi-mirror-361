import { useState } from "react";

const { utils } = Whitebox;

const InputContentArea = ({
  leftIcon = null,
  rightIcon = null,
  className = null,
  required = false,
  borderClass = null,
  ...props
}) => {
  const computedInputClassName = utils.getClasses(
    "input-content-area",
    "flex items-center gap-2 h-6 flex-1",
    className
  );

  const [hasFocus, setHasFocus] = useState(false);

  if (!borderClass)
    borderClass = hasFocus
      ? "border-surface-primary"
      : "border-borders-default";

  const containerClasses = utils.getClasses(
    "flex p-4 align-start gap-4",
    "border border-solid rounded-full border-borders-default",
    "self-stretch max-h-16",
    borderClass
  );

  return (
    <div className={containerClasses}>
      {leftIcon}

      <input
        type="text"
        className={computedInputClassName}
        required={required}
        onFocus={() => setHasFocus(true)}
        onBlur={() => setHasFocus(false)}
        {...props}
      />

      {rightIcon}
    </div>
  );
};

export { InputContentArea };
export default InputContentArea;
