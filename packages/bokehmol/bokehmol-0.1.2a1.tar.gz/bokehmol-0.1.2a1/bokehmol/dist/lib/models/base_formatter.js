import { CustomJSHover } from "@bokehjs/models/tools/inspectors/customjs_hover";
export class BaseFormatter extends CustomJSHover {
    static __name__ = "BaseFormatter";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "bokehmol.models.base_formatter";
    static {
        this.define(({ Int }) => ({
            width: [Int, 160],
            height: [Int, 120],
        }));
    }
    draw_svg(smiles) {
        smiles;
        return "";
    }
    format(value, format, special_vars) {
        format;
        special_vars;
        return this.draw_svg(value);
    }
}
//# sourceMappingURL=base_formatter.js.map