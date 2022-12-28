window.onload = function () {
  document.getElementById("download").addEventListener("click", () => {
    const data = this.document.getElementById("data");
    console.log(data);
    html2pdf().from(data).save();
  });
};
