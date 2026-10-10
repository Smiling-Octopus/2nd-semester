(function() {
    try {
        var statusField = this.getField("test_status");
        if (statusField) {
            statusField.value = "JS_EXECUTED";
        }
    } catch (e) {}

    try {
        var typeField = this.getField("viewer_type");
        if (typeField) {
            if (typeof app !== "undefined" && app.viewerType !== undefined) {
                typeField.value = String(app.viewerType);
            } else {
                typeField.value = "UNKNOWN";
            }
        }
    } catch (e) {
        var typeField = this.getField("viewer_type");
        if (typeField) {
            typeField.value = "UNKNOWN";
        }
    }

    try {
        var versionField = this.getField("viewer_version");
        if (versionField) {
            if (typeof app !== "undefined" && app.viewerVersion !== undefined) {
                versionField.value = String(app.viewerVersion);
            } else {
                versionField.value = "UNKNOWN";
            }
        }
    } catch (e) {
        var versionField = this.getField("viewer_version");
        if (versionField) {
            versionField.value = "UNKNOWN";
        }
    }

    try {
        var variationField = this.getField("viewer_variation");
        if (variationField) {
            if (typeof app !== "undefined" && app.viewerVariation !== undefined) {
                variationField.value = String(app.viewerVariation);
            } else {
                variationField.value = "UNKNOWN";
            }
        }
    } catch (e) {
        var variationField = this.getField("viewer_variation");
        if (variationField) {
            variationField.value = "UNKNOWN";
        }
    }
}).call(this);