import { forwardRef } from "react";
const StubIcon = forwardRef<SVGSVGElement>((props, ref) => <svg ref={ref} {...props} />);
StubIcon.displayName = "StubIcon";
export default StubIcon;
