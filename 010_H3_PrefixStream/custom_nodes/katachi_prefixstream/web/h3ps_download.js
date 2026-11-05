import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

async function downloadFiles(files) {
  for (const f of files) {
    const params = new URLSearchParams({ filename: f.filename, subfolder: f.subfolder, type: f.type || "output" });
    const res = await api.fetchApi(`/view?${params.toString()}`);
    if (!res.ok) { alert(`ダウンロードできませんでした: ${f.filename}`); continue; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = f.save_as || f.filename;  // 素材箱の名前とクリップ名を付けて、同じ名前が重ならないようにします
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    await new Promise((r) => setTimeout(r, 600));
  }
}

app.registerExtension({
  name: "aikatachi.p06.download",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "H3PSDownloadClip" && nodeData.name !== "H3PSJoinChain") return;
    const isJoin = nodeData.name === "H3PSJoinChain";
    const onCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = onCreated?.apply(this, arguments);
      this.h3psFiles = null;
      const label = isJoin ? "⬇ つないだ動画をダウンロード" : "⬇ この1本をダウンロード（動画＋途中の状態）";
      const btn = this.addWidget("button", label, null, async () => {
        let files = this.h3psFiles;
        if ((!files || !files.length) && isJoin) { alert("先に Run して、つないだ動画を作ってください"); return; }
        if (!files || !files.length) {
          const project = this.widgets?.find((w) => w.name === "project_name")?.value || "my_video";
          const res = await api.fetchApi(`/h3ps/latest_files?project=${encodeURIComponent(project)}`);
          const data = await res.json();
          if (!res.ok) { alert(data.error || "ファイルが見つかりません"); return; }
          files = data.files;
        }
        if (!files.length) { alert("ダウンロードできるファイルがありません"); return; }
        await downloadFiles(files);
      });
      if (btn) { btn.serialize = false; btn.options = { ...(btn.options || {}), serialize: false }; }
      return r;
    };
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      onExecuted?.apply(this, arguments);
      if (message?.h3ps_files) this.h3psFiles = message.h3ps_files;
    };
  },
});
