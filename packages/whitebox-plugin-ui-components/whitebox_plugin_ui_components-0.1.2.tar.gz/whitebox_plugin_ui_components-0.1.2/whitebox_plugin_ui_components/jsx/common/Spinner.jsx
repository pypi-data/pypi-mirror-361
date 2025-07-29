const { importWhiteboxComponent, utils } = Whitebox;
const IconSpinner = importWhiteboxComponent("icons.spinner");

const Spinner = ({ className, ...props }) => {
  const classes = utils.getClasses("animate-spin", className);
  return <IconSpinner className={classes} {...props} />;
};

export { Spinner };
export default Spinner;
