import { BaseFormatter } from "./base_formatter";
export class SmilesDrawerFormatter extends BaseFormatter {
    static __name__ = "SmilesDrawerFormatter";
    SmiDrawer;
    drawer;
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "bokehmol.models.smilesdrawer_formatter";
    static {
        this.define(({ Str, Dict, Unknown }) => ({
            theme: [Str, "light"],
            background_colour: [Str, "transparent"],
            mol_options: [Dict(Unknown), {}],
            reaction_options: [Dict(Unknown), {}],
        }));
    }
    initialize() {
        super.initialize();
        // @ts-ignore
        this.SmiDrawer = SmiDrawer;
    }
    _make_svg_element() {
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        svg.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
        svg.setAttributeNS(null, "width", "" + this.width);
        svg.setAttributeNS(null, "height", "" + this.height);
        svg.style.backgroundColor = this.background_colour;
        return svg;
    }
    _setup_drawer() {
        // @ts-ignore
        const sd = new this.SmiDrawer(this.mol_options, this.reaction_options);
        this.drawer = sd;
        return sd;
    }
    draw_svg(smiles) {
        const sd = this.drawer ?? this._setup_drawer();
        const target = this._make_svg_element();
        sd.draw(smiles, target, this.theme);
        const svg = target.outerHTML;
        target.remove();
        return svg;
    }
}
//# sourceMappingURL=smilesdrawer_formatter.js.map