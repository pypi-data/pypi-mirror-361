/**
 * @fileoverview Set a mol* viewer to visualize the benchmarl results.. 
 * @author Lucas ROUAUD
 * @version 0.0.1
 * @date 15-07-2024
 * @license MIT
 */

// Fetch data from the URL to display PDB from the benchmark.
let url = window.location.href;

let pdb_id_vam = "1AKX";
let field_val = "h_b_acceptor";

if (url.includes("?")) {
    process_url = url.split("?");
    process_url = process_url[process_url.length - 1];

    process_url.split("&").forEach((field) => {
        let [key, value] = field.split("=");

        if (key == "pdb_id") {
            pdb_id_val = value;
        } else if (key == "field") {
            field_val = value;
        }
    });
}

// Setup the molstar viewer.
let result = molstar.Viewer.create("app-id", {
    emdbProvider: "rcsb",
    pdbProvider: "rcsb",
    layoutIsExpanded: false,
    layoutShowSequence: false,
    emdbProvider: "rcsb",
    layoutShowLeftPanel: true,
    layoutShowRemoteState: false,
    viewportShowAnimation: false,
    layoutShowSequence: false,
    viewportShowSelectionMode: false,
    layoutShowLog: true,
    viewportShowExpand: true,
    layoutShowControls: false,
}).then((viewer) => {
    viewer.loadStructureFromUrl(
        (url = `https://smiffer.mol3d.tech/data/${pdb_id_val}/` +
            `input/${pdb_id_val}.pdb`),
        (format = "pdb")
    );

    viewer.loadVolumeFromUrl(
        {
            url: `https://smiffer.mol3d.tech/data/${pdb_id_val}/` +
                `output/${pdb_id_val}_${field_val}.dx`,
            format: "dx",
            isBinary: false,
        },
        [
            {
                type: "relative",
                value: 0,
            },
        ],
        {
            isLazy: false,
        }
    );
});
