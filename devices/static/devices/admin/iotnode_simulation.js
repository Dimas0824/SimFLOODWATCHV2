(function () {
  function attachRangeOutput(input) {
    const outputId = input.dataset.rangeOutput;
    if (!outputId) {
      return;
    }

    let output = document.getElementById(outputId);
    if (!output) {
      output = document.createElement("div");
      output.id = outputId;
      output.style.marginTop = "6px";
      output.style.fontSize = "12px";
      output.style.color = "#666";
      input.insertAdjacentElement("afterend", output);
    }

    const sync = function () {
      const suffix = input.id === "id_simulation_drift_bias_cm" ? " cm bias" : " cm";
      output.textContent = "Nilai: " + input.value + suffix;
    };

    input.addEventListener("input", sync);
    sync();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document
      .querySelectorAll("input[type='range'][data-range-output]")
      .forEach(attachRangeOutput);
  });
})();
