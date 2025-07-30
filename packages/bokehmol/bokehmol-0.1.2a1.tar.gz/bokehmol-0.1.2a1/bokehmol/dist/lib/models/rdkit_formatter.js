import { BaseFormatter } from "./base_formatter";
export class RDKitFormatter extends BaseFormatter {
    static __name__ = "RDKitFormatter";
    RDKitModule;
    json_draw_opts;
    json_mol_opts;
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "bokehmol.models.rdkit_formatter";
    static {
        this.define(({ Bool, Dict, Unknown }) => ({
            prefer_coordgen: [Bool, true],
            remove_hs: [Bool, true],
            sanitize: [Bool, true],
            kekulize: [Bool, true],
            draw_options: [Dict(Unknown), {}],
        }));
    }
    initialize() {
        super.initialize();
        // @ts-expect-error
        initRDKitModule().then((RDKitModule) => {
            this.RDKitModule = RDKitModule;
            console.log("RDKit version: " + RDKitModule.version());
        });
    }
    _wait_rdkit_module() {
        // blocks until the rdkit module is available
        if (typeof this.RDKitModule === "undefined") {
            setTimeout(this._wait_rdkit_module, 100);
        }
    }
    _setup_options() {
        this._wait_rdkit_module();
        this.RDKitModule.prefer_coordgen(this.prefer_coordgen);
        this.json_mol_opts = JSON.stringify({
            removeHs: this.remove_hs,
            sanitize: this.sanitize,
            kekulize: this.kekulize,
        });
        this.json_draw_opts = JSON.stringify({
            width: this.width,
            height: this.height,
            ...this.draw_options,
        });
        return this.json_draw_opts;
    }
    draw_svg(smiles) {
        const draw_opts = this.json_draw_opts ?? this._setup_options();
        const mol = this.RDKitModule.get_mol(smiles, this.json_mol_opts);
        if (mol !== null && mol.is_valid()) {
            const svg = mol.get_svg_with_highlights(draw_opts);
            mol.delete();
            return svg;
        }
        return super.draw_svg(smiles);
    }
}
//# sourceMappingURL=rdkit_formatter.js.map