const API_BASE = "";

// ============================================================
// FORM ELEMENTS
// ============================================================

const sofaTypeSelect = document.getElementById("sofaType");
const sofaModelSelect = document.getElementById("sofaModel");

const lengthInput = document.getElementById("length");
const depthInput = document.getElementById("depth");
const heightInput = document.getElementById("height");

const customerNameInput = document.getElementById("customerName");
const customerContactInput = document.getElementById("customerContact");

const imageInput = document.getElementById("sofaImage");
const imagePreview = document.getElementById("imagePreview");
const imagePreviewContainer = document.getElementById(
    "imagePreviewContainer"
);

const calculateButton = document.getElementById("calculateButton");
const statusMessage = document.getElementById("statusMessage");
const quotationSection = document.getElementById(
    "quotationSection"
);

// ============================================================
// APPLICATION DATA
// ============================================================

let sofaModels = [];


// ============================================================
// LOAD SOFA TYPES
// ============================================================

async function loadSofaTypes() {
    try {
        const response = await fetch(
            `${API_BASE}/sofas/types`
        );

        if (!response.ok) {
            throw new Error(
                "Unable to load sofa types."
            );
        }

        const types = await response.json();

        sofaTypeSelect.innerHTML =
            '<option value="">Select sofa type</option>';

        types.forEach((type) => {
            const option =
                document.createElement("option");

            option.value = type.sofa_type_id;

            option.textContent =
                `${type.sofa_type} ` +
                `(${type.seating_capacity} seat)`;

            sofaTypeSelect.appendChild(option);
        });

    } catch (error) {
        showStatus(error.message, true);
    }
}


// ============================================================
// LOAD ALL SOFA MODELS
// ============================================================

async function loadSofaModels() {
    try {
        const response = await fetch(
            `${API_BASE}/sofas/models`
        );

        if (!response.ok) {
            throw new Error(
                "Unable to load sofa models."
            );
        }

        sofaModels = await response.json();

    } catch (error) {
        showStatus(error.message, true);
    }
}


// ============================================================
// LOAD MODELS BASED ON SOFA TYPE
// ============================================================

function loadModelsForType() {

    const selectedTypeId =
        Number(sofaTypeSelect.value);

    sofaModelSelect.innerHTML =
        '<option value="">Select sofa model</option>';

    sofaModelSelect.disabled = true;

    // Clear dimensions
    lengthInput.value = "";
    depthInput.value = "";
    heightInput.value = "";

    if (!selectedTypeId) {
        return;
    }

    const filteredModels =
        sofaModels.filter(
            (model) =>
                model.sofa_type_id === selectedTypeId
        );

    filteredModels.forEach((model) => {

        const option =
            document.createElement("option");

        option.value =
            model.sofa_model_id;

        option.textContent =
            `${model.sofa_id} — ` +
            `${model.sofa_type} — ` +
            `${model.length_mm} × ` +
            `${model.depth_mm} × ` +
            `${model.height_mm} mm`;

        sofaModelSelect.appendChild(option);
    });

    sofaModelSelect.disabled =
        filteredModels.length === 0;

    if (filteredModels.length === 0) {
        showStatus(
            "No sofa models available for this type.",
            true
        );
    }
}


// ============================================================
// LOAD MODEL DIMENSIONS
// ============================================================

function loadModelDimensions() {

    const modelId =
        Number(sofaModelSelect.value);

    const model =
        sofaModels.find(
            (item) =>
                item.sofa_model_id === modelId
        );

    if (!model) {
        return;
    }

    lengthInput.value =
        model.length_mm;

    depthInput.value =
        model.depth_mm;

    heightInput.value =
        model.height_mm;

    showStatus(
        "Sofa model selected. Dimensions loaded."
    );
}


// ============================================================
// IMAGE PREVIEW
// ============================================================

function handleImagePreview() {

    const file =
        imageInput.files[0];

    if (!file) {

        imagePreviewContainer.classList.add(
            "hidden"
        );

        imagePreview.removeAttribute("src");

        return;
    }

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    if (!allowedTypes.includes(file.type)) {

        imageInput.value = "";

        imagePreviewContainer.classList.add(
            "hidden"
        );

        showStatus(
            "Only JPG, PNG or WEBP images are allowed.",
            true
        );

        return;
    }

    const reader =
        new FileReader();

    reader.onload =
        function (event) {

            imagePreview.src =
                event.target.result;

            imagePreviewContainer.classList.remove(
                "hidden"
            );
        };

    reader.readAsDataURL(file);
}


// ============================================================
// STATUS MESSAGE
// ============================================================

function showStatus(
    message,
    isError = false
) {

    statusMessage.textContent =
        message;

    statusMessage.style.color =
        isError
            ? "#dc2626"
            : "#2563eb";
}


// ============================================================
// CURRENCY FORMAT
// ============================================================

function formatCurrency(value) {

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    ).format(
        Number(value || 0)
    );
}


// ============================================================
// NUMBER FORMAT
// ============================================================

function formatNumber(value) {

    return Number(
        value || 0
    ).toFixed(3);
}


// ============================================================
// DISPLAY QUOTATION
// ============================================================

function displayQuotation(data) {

    quotationSection.classList.remove(
        "hidden"
    );

    // --------------------------------------------------------
    // QUOTATION NUMBER
    // --------------------------------------------------------

    document.getElementById(
        "quotationNumber"
    ).textContent =
        `Quotation No: ${data.quotation_number}`;


    // --------------------------------------------------------
    // TOTAL
    // --------------------------------------------------------

    document.getElementById(
        "finalTotal"
    ).textContent =
        formatCurrency(
            data.total_inr
        );

    document.getElementById(
        "quotationTotal"
    ).textContent =
        formatCurrency(
            data.total_inr
        );


    // --------------------------------------------------------
    // COST BREAKDOWN
    // --------------------------------------------------------

    document.getElementById(
        "materialCost"
    ).textContent =
        formatCurrency(
            data.material_cost_inr
        );

    document.getElementById(
        "labourCost"
    ).textContent =
        formatCurrency(
            data.labour_cost_inr
        );

    document.getElementById(
        "stitchingCost"
    ).textContent =
        formatCurrency(
            data.stitching_cost_inr
        );

    document.getElementById(
        "overheadCost"
    ).textContent =
        formatCurrency(
            data.overhead_inr
        );

    document.getElementById(
        "transportationCost"
    ).textContent =
        formatCurrency(
            data.transportation_cost_inr
        );

    document.getElementById(
        "profitCost"
    ).textContent =
        formatCurrency(
            data.profit_inr
        );


    // --------------------------------------------------------
    // SOFA INFORMATION
    // --------------------------------------------------------

    if (data.sofa) {

        document.getElementById(
            "resultSofa"
        ).textContent =
            `${data.sofa.sofa_id} — ` +
            `${data.sofa.sofa_type}`;

        document.getElementById(
            "resultDimensions"
        ).textContent =
            `${data.sofa.length_mm} × ` +
            `${data.sofa.depth_mm} × ` +
            `${data.sofa.height_mm} mm`;
    }


    // --------------------------------------------------------
    // SCALE FACTORS
    // --------------------------------------------------------

    if (data.scale_factors) {

        document.getElementById(
            "scaleLength"
        ).textContent =
            formatNumber(
                data.scale_factors.SL
            );

        document.getElementById(
            "scaleDepth"
        ).textContent =
            formatNumber(
                data.scale_factors.SW
            );

        document.getElementById(
            "scaleHeight"
        ).textContent =
            formatNumber(
                data.scale_factors.SH
            );
    }


    // --------------------------------------------------------
    // BOM TABLE
    // --------------------------------------------------------

    const tableBody =
        document.getElementById(
            "bomTableBody"
        );

    tableBody.innerHTML = "";


    if (
        data.items &&
        data.items.length > 0
    ) {

        data.items.forEach(
            (item) => {

                const row =
                    document.createElement("tr");

                row.innerHTML = `
                    <td>
                        ${
                            item.component_name ||
                            `Component ${item.component_id}`
                        }
                    </td>

                    <td>
                        ${
                            item.material_name ||
                            `Material ${item.material_id}`
                        }
                    </td>

                    <td>
                        ${formatNumber(item.quantity)}
                    </td>

                    <td>
                        ${item.unit || "-"}
                    </td>

                    <td>
                        ${formatCurrency(
                            item.unit_price_inr
                        )}
                    </td>

                    <td>${formatCurrency(
    item.total_inr ?? item.total ?? item.total_cost_inr
)}</td>
                `;

                tableBody.appendChild(row);
            }
        );

    } else {

        const row =
            document.createElement("tr");

        row.innerHTML = `
            <td colspan="6">
                No BOM items available.
            </td>
        `;

        tableBody.appendChild(row);
    }


    // --------------------------------------------------------
    // SCROLL TO QUOTATION
    // --------------------------------------------------------

    quotationSection.scrollIntoView({
        behavior: "smooth"
    });
}


// ============================================================
// UPLOAD IMAGE
// ============================================================

async function uploadSofaImage(file) {

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    const response =
        await fetch(
            `${API_BASE}/images/upload`,
            {
                method: "POST",
                body: formData
            }
        );

    const data =
        await response.json();

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Image upload failed."
        );
    }

    return data;
}


// ============================================================
// CALCULATE QUOTATION
// ============================================================

async function calculateQuotation() {

    const sofaModelId =
        Number(
            sofaModelSelect.value
        );

    const length =
        Number(
            lengthInput.value
        );

    const depth =
        Number(
            depthInput.value
        );

    const height =
        Number(
            heightInput.value
        );


    // --------------------------------------------------------
    // VALIDATION
    // --------------------------------------------------------

    if (!sofaModelId) {

        showStatus(
            "Please select a sofa model.",
            true
        );

        return;
    }

    if (
        !length ||
        !depth ||
        !height
    ) {

        showStatus(
            "Please enter valid length, depth and height.",
            true
        );

        return;
    }


    calculateButton.disabled =
        true;

    quotationSection.classList.add(
        "hidden"
    );


    try {

        // ----------------------------------------------------
        // IMAGE UPLOAD
        // ----------------------------------------------------

        let imagePath = null;

        const selectedImage =
            imageInput.files[0];

        if (selectedImage) {

            showStatus(
                "Uploading sofa image..."
            );

            const uploadData =
                await uploadSofaImage(
                    selectedImage
                );

            imagePath =
                uploadData.image_path;

            console.log(
                "Image uploaded:",
                imagePath
            );
        }


        // ----------------------------------------------------
        // QUOTATION REQUEST
        // ----------------------------------------------------

        showStatus(
            "Calculating sofa cost..."
        );


        const requestData = {

            sofa_model_id:
                sofaModelId,

            length_mm:
                length,

            depth_mm:
                depth,

            height_mm:
                height,

            image_path:
                imagePath,

            customer_name:
                customerNameInput.value.trim() ||
                null,

            customer_contact:
                customerContactInput.value.trim() ||
                null
        };


        console.log(
            "Quotation request:",
            requestData
        );


        // ----------------------------------------------------
        // CALL QUOTATION API
        // ----------------------------------------------------

        const response =
            await fetch(
                `${API_BASE}/quotations/calculate`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            requestData
                        )
                }
            );


        const data =
            await response.json();


        // ----------------------------------------------------
        // API ERROR
        // ----------------------------------------------------

        if (!response.ok) {

            let message =
                "Quotation calculation failed.";

            if (data.detail) {

                if (
                    typeof data.detail ===
                    "string"
                ) {

                    message =
                        data.detail;

                } else if (
                    data.detail.message
                ) {

                    message =
                        data.detail.message;
                }
            }

            throw new Error(
                message
            );
        }


        // ----------------------------------------------------
        // DISPLAY RESULT
        // ----------------------------------------------------

        displayQuotation(
            data
        );


        showStatus(
            "Quotation calculated successfully."
        );


        // ----------------------------------------------------
        // DEBUG INFORMATION
        // ----------------------------------------------------

        console.log(
            "Quotation response:",
            data
        );

        console.log(
            "Uploaded image path:",
            imagePath
        );


    } catch (error) {

        console.error(
            "Quotation error:",
            error
        );

        showStatus(
            error.message ||
            "Something went wrong.",
            true
        );

    } finally {

        calculateButton.disabled =
            false;
    }
}


// ============================================================
// EVENT LISTENERS
// ============================================================

sofaTypeSelect.addEventListener(
    "change",
    loadModelsForType
);

sofaModelSelect.addEventListener(
    "change",
    loadModelDimensions
);

imageInput.addEventListener(
    "change",
    handleImagePreview
);

calculateButton.addEventListener(
    "click",
    calculateQuotation
);


// ============================================================
// APPLICATION INITIALIZATION
// ============================================================

async function initializeApplication() {

    showStatus(
        "Loading sofa data..."
    );

    await loadSofaTypes();

    await loadSofaModels();

    showStatus(
        "Ready. Select a sofa type."
    );
}


// ============================================================
// START APPLICATION
// ============================================================

initializeApplication();