import React, { useState, useEffect, useCallback, useRef } from "react";
import * as Flow from "flow-sdk";

// ---------------------------------------------------------------------------
// Constants & Types
// ---------------------------------------------------------------------------
const STORAGE_KEY = "VP_OMNI_STUDIO_V2_STATE";
const MODEL_IMAGE = "🍌 Nano Banana 2.1";
const MODEL_VIDEO = "Omni 1.1 Flash";

type EngineMode = "hybrid_video" | "zero_credit_flipbook";
type SceneStatus = "IDLE" | "QUEUED" | "GENERATING_IMAGE" | "IMAGE_READY" | "GENERATING_VIDEO" | "VIDEO_READY" | "ERROR";

interface ReferenceAsset {
  mediaId: string;
  base64?: string;
  mimeType?: string;
  name?: string;
}

interface SceneBeat {
  id: string;
  sceneId: string;
  narration: string;
  visualPrompt: string;
  durationSeconds: number;
  omniDuration: 4 | 6 | 8 | 10;
  keyframeMediaId: string | null;
  keyframeBase64: string | null;
  videoMediaId: string | null;
  status: SceneStatus;
  error?: string;
}

interface StudioState {
  version: string;
  mode: EngineMode;
  aspectRatio: "16:9" | "9:16";
  scriptText: string;
  characterRef: ReferenceAsset | null;
  styleRef: ReferenceAsset | null;
  scenes: SceneBeat[];
  isProcessing: boolean;
  statusMessage: string;
}

const DEFAULT_SCRIPT = `Nhiều người nghĩ rằng làm việc chăm chỉ là cách duy nhất để tự do tài chính.
Nhưng thực tế, đòn bẩy thông minh mới là chìa khóa bứt phá.
Khi bạn sở hữu một hệ thống vận hành tự động, thời gian sẽ đứng về phía bạn.
Đừng bán thời gian lấy tiền, hãy xây dựng cỗ máy tạo ra dòng tiền bền vững.`;

// ---------------------------------------------------------------------------
// Helper: Resolve Omni 1.1 Flash Auto-Duration (4s | 6s | 8s | 10s)
// ---------------------------------------------------------------------------
function resolveOmniDuration(seconds: number): 4 | 6 | 8 | 10 {
  if (seconds <= 4) return 4;
  if (seconds <= 6) return 6;
  if (seconds <= 8) return 8;
  return 10;
}

export default function App() {
  const [state, setState] = useState<StudioState>({
    version: "2.0.0",
    mode: "hybrid_video",
    aspectRatio: "16:9",
    scriptText: DEFAULT_SCRIPT,
    characterRef: null,
    styleRef: null,
    scenes: [],
    isProcessing: false,
    statusMessage: "Hệ thống sẵn sàng. V2 Omni Chain Studio khởi động hoàn tất."
  });

  const stateRef = useRef(state);
  stateRef.current = state;

  // -------------------------------------------------------------------------
  // Atomic State Persistence via Flow.storage
  // -------------------------------------------------------------------------
  const persistState = useCallback(async (nextState: StudioState) => {
    setState(nextState);
    try {
      await Flow.storage.setItem(STORAGE_KEY, {
        version: nextState.version,
        mode: nextState.mode,
        aspectRatio: nextState.aspectRatio,
        scriptText: nextState.scriptText,
        characterRef: nextState.characterRef,
        styleRef: nextState.styleRef,
        scenes: nextState.scenes.map(s => ({
          ...s,
          // Strip heavy base64 strings in persistent storage if too large
          keyframeBase64: s.keyframeBase64 ? s.keyframeBase64.slice(0, 500) + "..." : null
        }))
      });
    } catch {
      // Fallback to local storage if host storage has transient quota limits
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(nextState));
      } catch {}
    }
  }, []);

  // Load state on mount
  useEffect(() => {
    (async () => {
      try {
        const saved = await Flow.storage.getItem(STORAGE_KEY);
        if (saved && typeof saved === "object") {
          setState(prev => ({
            ...prev,
            ...(saved as Partial<StudioState>),
            isProcessing: false,
            statusMessage: "Đã khôi phục trạng thái làm việc từ Flow Storage."
          }));
          return;
        }
      } catch {}

      try {
        const local = localStorage.getItem(STORAGE_KEY);
        if (local) {
          setState(prev => ({ ...prev, ...JSON.parse(local), isProcessing: false }));
        }
      } catch {}
    })();
  }, []);

  // -------------------------------------------------------------------------
  // 1. AI Script-to-Beats Splitter via Flow.generate.text (0 credits)
  // -------------------------------------------------------------------------
  const handleSplitScript = async () => {
    if (!state.scriptText.trim()) return;

    setState(prev => ({
      ...prev,
      isProcessing: true,
      statusMessage: "Đang phân tích kịch bản bằng AI Gemini (0 credits)..."
    }));

    try {
      const prompt = `Bạn là đạo diễn kịch bản Video Pilot (2D Doodle Explainer).
Hãy chia kịch bản sau thành các phân cảnh trực quan (Storyboard Beats).
Mỗi phân cảnh cần:
- sceneId: mã cảnh (01, 02, 03...)
- narration: câu thoại ngắn gọn, súc tích (tiếng Việt)
- visualPrompt: mô tả hình vẽ 2D Doodle tối giản theo phong cách Feynman (#000000 marker, bald circle stickman, #3B82C4 shirt, flat canvas #F8F0DC, >=60% negative space)
- durationSeconds: thời lượng ước tính (từ 3 đến 10 giây)

KỊCH BẢN:
\"\"\"
${state.scriptText}
\"\"\"

Chỉ trả về DUY NHẤT một mảng JSON hợp lệ dạng:
[
  {
    "sceneId": "01",
    "narration": "...",
    "visualPrompt": "2D doodle stickman with #3B82C4 shirt looking at a financial chart on flat #F8F0DC canvas",
    "durationSeconds": 5
  }
]`;

      const res = await Flow.generate.text({
        prompt,
        systemInstruction: "You are a professional Video Pilot storyboard planner. Output JSON only."
      });

      let jsonText = res.text.trim();
      if (jsonText.startsWith("```json")) {
        jsonText = jsonText.replace(/^```json/, "").replace(/```$/, "").trim();
      } else if (jsonText.startsWith("```")) {
        jsonText = jsonText.replace(/^```/, "").replace(/```$/, "").trim();
      }

      let parsed: any[] = [];
      try {
        parsed = JSON.parse(jsonText);
      } catch {
        // Fallback: Line-by-line parsing
        const lines = state.scriptText.split("\n").filter(l => l.trim().length > 0);
        parsed = lines.map((line, idx) => ({
          sceneId: String(idx + 1).padStart(2, "0"),
          narration: line.trim(),
          visualPrompt: `2D doodle stickman in #3B82C4 shirt demonstrating metaphor for: ${line.trim()} on flat clean background`,
          durationSeconds: 5
        }));
      }

      const newScenes: SceneBeat[] = parsed.map((item, idx) => {
        const dur = Number(item.durationSeconds) || 5;
        return {
          id: `BEAT-${Date.now()}-${idx}`,
          sceneId: String(item.sceneId || idx + 1).padStart(2, "0"),
          narration: String(item.narration || ""),
          visualPrompt: String(item.visualPrompt || ""),
          durationSeconds: dur,
          omniDuration: resolveOmniDuration(dur),
          keyframeMediaId: null,
          keyframeBase64: null,
          videoMediaId: null,
          status: "IDLE"
        };
      });

      await persistState({
        ...stateRef.current,
        scenes: newScenes,
        isProcessing: false,
        statusMessage: `Đã phân tách thành công ${newScenes.length} phân cảnh Storyboard.`
      });
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        isProcessing: false,
        statusMessage: `Lỗi phân tích kịch bản: ${err.message || String(err)}`
      }));
    }
  };

  // -------------------------------------------------------------------------
  // 2. Reference Selection Lock (Flow.media.select)
  // -------------------------------------------------------------------------
  const handleSelectReference = async (type: "character" | "style") => {
    try {
      const asset = await Flow.media.select({ filter: "image" });
      if (!asset) return;

      const refAsset: ReferenceAsset = {
        mediaId: asset.mediaId,
        base64: asset.base64,
        mimeType: asset.mimeType,
        name: type === "character" ? "Nhân vật Stickman" : "Phong cách Doodle"
      };

      await persistState({
        ...stateRef.current,
        characterRef: type === "character" ? refAsset : stateRef.current.characterRef,
        styleRef: type === "style" ? refAsset : stateRef.current.styleRef,
        statusMessage: `Đã khoá ${type === "character" ? "nhân vật" : "phong cách"} thành công (Media ID: ${asset.mediaId.slice(-6)}).`
      });
    } catch (err: any) {
      setState(prev => ({ ...prev, statusMessage: `Lỗi chọn reference: ${err.message}` }));
    }
  };

  const handleClearReference = async (type: "character" | "style") => {
    await persistState({
      ...stateRef.current,
      characterRef: type === "character" ? null : stateRef.current.characterRef,
      styleRef: type === "style" ? null : stateRef.current.styleRef,
      statusMessage: `Đã xoá tham chiếu ${type}.`
    });
  };

  // -------------------------------------------------------------------------
  // 3. Batch 0-Credit Keyframe Generator (Flow.generate.image)
  // -------------------------------------------------------------------------
  const handleGenerateKeyframes = async () => {
    const curScenes = stateRef.current.scenes;
    if (curScenes.length === 0) return;

    setState(prev => ({
      ...prev,
      isProcessing: true,
      statusMessage: "Bắt đầu sinh hàng loạt Keyframe với Nano Banana 2.1 (0 credits)..."
    }));

    const refIds: string[] = [];
    if (stateRef.current.characterRef?.mediaId) refIds.push(stateRef.current.characterRef.mediaId);
    if (stateRef.current.styleRef?.mediaId) refIds.push(stateRef.current.styleRef.mediaId);

    const updatedScenes = [...curScenes];

    for (let i = 0; i < updatedScenes.length; i++) {
      const sc = updatedScenes[i];
      if (sc.keyframeMediaId) continue; // Skip if already generated

      sc.status = "GENERATING_IMAGE";
      setState(prev => ({
        ...prev,
        scenes: [...updatedScenes],
        statusMessage: `Đang vẽ cảnh ${sc.sceneId}/${updatedScenes.length} (0 credits)...`
      }));

      try {
        const fullPrompt = `2D handdrawn doodle explainer, Feynman visual metaphor: ${sc.visualPrompt}, bold wobbly #000000 marker line, bald circle stickman wearing #3B82C4 shirt, flat canvas #F8F0DC, minimal aesthetic, 60% negative space, zero 3D, zero shadows.`;
        const res = await Flow.generate.image({
          prompt: fullPrompt,
          modelDisplayName: MODEL_IMAGE,
          referenceImageMediaIds: refIds.length > 0 ? refIds : undefined,
          aspectRatio: stateRef.current.aspectRatio
        });

        sc.keyframeMediaId = res.mediaId;
        sc.keyframeBase64 = res.base64 || null;
        sc.status = "IMAGE_READY";
      } catch (err: any) {
        sc.status = "ERROR";
        sc.error = err.message || "Lỗi tạo ảnh";
      }
    }

    await persistState({
      ...stateRef.current,
      scenes: updatedScenes,
      isProcessing: false,
      statusMessage: "Hoàn tất sinh toàn bộ Keyframe với 0 credits!"
    });
  };

  // -------------------------------------------------------------------------
  // 4A. Mode 1: Omni 1.1 Flash Video Chain (Flow.generate.video)
  // -------------------------------------------------------------------------
  const handleRunOmniVideoChain = async () => {
    const curScenes = stateRef.current.scenes;
    if (curScenes.length === 0) return;

    setState(prev => ({
      ...prev,
      isProcessing: true,
      statusMessage: "Bắt đầu chuỗi sinh Video Omni 1.1 Flash Auto-Duration..."
    }));

    const updatedScenes = [...curScenes];

    for (let i = 0; i < updatedScenes.length; i++) {
      const sc = updatedScenes[i];
      if (!sc.keyframeMediaId) continue;
      if (sc.videoMediaId) continue;

      // Next keyframe for Start+End frame interpolation
      const nextScene = updatedScenes[i + 1];
      const endFrameId = nextScene?.keyframeMediaId || undefined;

      sc.status = "GENERATING_VIDEO";
      setState(prev => ({
        ...prev,
        scenes: [...updatedScenes],
        statusMessage: `Đang sinh video cảnh ${sc.sceneId} (${sc.omniDuration}s) với Omni 1.1 Flash...`
      }));

      try {
        const videoPrompt = `Smooth cinematic camera transition, 2D doodle animation: ${sc.narration}. Continuous character movement, clean flat aesthetic.`;
        const res = await Flow.generate.video({
          prompt: videoPrompt,
          modelDisplayName: MODEL_VIDEO,
          firstFrameImageMediaId: sc.keyframeMediaId,
          lastFrameImageMediaId: endFrameId,
          durationSeconds: sc.omniDuration,
          aspectRatio: stateRef.current.aspectRatio
        });

        sc.videoMediaId = res.mediaId;
        sc.status = "VIDEO_READY";
      } catch (err: any) {
        sc.status = "ERROR";
        sc.error = err.message || "Lỗi tạo video";
      }
    }

    await persistState({
      ...stateRef.current,
      scenes: updatedScenes,
      isProcessing: false,
      statusMessage: "Hoàn tất chuỗi sinh video Omni 1.1 Flash!"
    });
  };

  // -------------------------------------------------------------------------
  // 4B. Mode 2: Zero-Credit Flipbook Storyboard Mode (Flow.save + Flow.download)
  // -------------------------------------------------------------------------
  const handleExportZeroCreditFlipbook = async () => {
    const curScenes = stateRef.current.scenes;
    if (curScenes.length === 0) return;

    setState(prev => ({
      ...prev,
      isProcessing: true,
      statusMessage: "Đang lưu Storyboard Keyframes sang Thư viện Dự án (Flow.save) với 0 credits..."
    }));

    try {
      // 1. Save each generated keyframe to Project Media Grid
      let savedCount = 0;
      for (const sc of curScenes) {
        if (sc.keyframeBase64) {
          await Flow.save({
            base64: sc.keyframeBase64,
            mimeType: "image/png",
            name: `VP_Scene_${sc.sceneId}_Keyframe.png`
          });
          savedCount++;
        }
      }

      // 2. Build and Download Manifest JSON
      const manifest = {
        title: "VP Omni Chain Storyboard Manifest",
        engine: "VP Omni Chain Studio V2",
        mode: "zero_credit_flipbook",
        cost: "0 credits",
        totalScenes: curScenes.length,
        savedKeyframes: savedCount,
        exportedAt: new Date().toISOString(),
        scenes: curScenes.map(sc => ({
          sceneId: sc.sceneId,
          narration: sc.narration,
          visualPrompt: sc.visualPrompt,
          durationSeconds: sc.durationSeconds,
          omniDuration: sc.omniDuration,
          keyframeMediaId: sc.keyframeMediaId
        }))
      };

      const jsonStr = JSON.stringify(manifest, null, 2);
      const b64Manifest = btoa(unescape(encodeURIComponent(jsonStr)));

      await Flow.download({
        base64: b64Manifest,
        mimeType: "application/json",
        filename: `VP_ZERO_CREDIT_STORYBOARD_${Date.now()}.json`
      });

      setState(prev => ({
        ...prev,
        isProcessing: false,
        statusMessage: `Đã lưu ${savedCount} ảnh vào Dự án và tải Manifest thành công (0 credits)!`
      }));
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        isProcessing: false,
        statusMessage: `Lỗi xuất Storyboard: ${err.message}`
      }));
    }
  };

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100 font-sans select-none overflow-hidden">
      {/* ------------------------------------------------------------------- */}
      {/* Top Header & Engine Mode Switch */}
      {/* ------------------------------------------------------------------- */}
      <header className="px-6 py-3.5 bg-zinc-900/90 border-b border-zinc-800 flex items-center justify-between shrink-0 shadow-lg backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-indigo-500/20 shadow-md">
            <span className="text-xl">🍌</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-black tracking-wide text-white uppercase">VP Omni Chain Studio V2</h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                0-Credit Ready
              </span>
            </div>
            <p className="text-[11px] font-medium text-zinc-400">
              Dual-Engine: Nano Banana 2.1 (0 cr) + Omni 1.1 Flash (4s/6s/8s/10s)
            </p>
          </div>
        </div>

        {/* Mode Switch Pills */}
        <div className="flex items-center gap-3 bg-zinc-950 p-1 rounded-xl border border-zinc-800">
          <button
            type="button"
            onClick={() => persistState({ ...state, mode: "hybrid_video" })}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              state.mode === "hybrid_video"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            <span>🎬</span> Mode 1: Omni Video Chain
          </button>
          <button
            type="button"
            onClick={() => persistState({ ...state, mode: "zero_credit_flipbook" })}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              state.mode === "zero_credit_flipbook"
                ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30"
                : "text-zinc-400 hover:text-white"
            }`}
          >
            <span>⚡</span> Mode 2: Zero-Credit Flipbook (0 cr)
          </button>
        </div>

        {/* Global Aspect Ratio & Status */}
        <div className="flex items-center gap-3">
          <select
            value={state.aspectRatio}
            onChange={e => persistState({ ...state, aspectRatio: e.target.value as "16:9" | "9:16" })}
            className="bg-zinc-800 text-xs font-semibold px-3 py-1.5 rounded-lg border border-zinc-700 outline-none cursor-pointer"
          >
            <option value="16:9">16:9 Explainer</option>
            <option value="9:16">9:16 Shorts / Reel</option>
          </select>
        </div>
      </header>

      {/* ------------------------------------------------------------------- */}
      {/* Main Studio Body: 2 Columns */}
      {/* ------------------------------------------------------------------- */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Column: Script & References (380px) */}
        <div className="w-96 border-r border-zinc-800 bg-zinc-900/40 p-5 flex flex-col gap-5 overflow-y-auto shrink-0">
          {/* Script Input */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold tracking-wider text-zinc-300 uppercase">Kịch bản câu chuyện</label>
              <span className="text-[10px] text-zinc-500 font-mono">Feynman Spoken Voice</span>
            </div>
            <textarea
              rows={6}
              value={state.scriptText}
              onChange={e => setState(prev => ({ ...prev, scriptText: e.target.value }))}
              placeholder="Nhập nội dung thoại hoặc kịch bản phân cảnh..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs text-zinc-200 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none resize-none leading-relaxed"
            />
            <button
              type="button"
              disabled={state.isProcessing}
              onClick={handleSplitScript}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs shadow-md transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <span>✨</span> Tách cảnh tự động qua AI (0 credits)
            </button>
          </div>

          {/* Reference Asset Locks */}
          <div className="flex flex-col gap-3 pt-3 border-t border-zinc-800">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold tracking-wider text-zinc-300 uppercase">Khoá mẫu hình ảnh</label>
              <span className="text-[10px] text-zinc-500">Identity & Style Lock</span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {/* Character Ref Slot */}
              <div className="flex flex-col gap-1.5">
                <span className="text-[11px] font-semibold text-zinc-400">Nhân vật (Stickman)</span>
                <div
                  onClick={() => !state.characterRef && handleSelectReference("character")}
                  className={`h-28 rounded-xl border-2 border-dashed flex flex-col items-center justify-center p-2 relative transition-all overflow-hidden ${
                    state.characterRef
                      ? "border-indigo-500 bg-indigo-950/20"
                      : "border-zinc-700 bg-zinc-950/60 hover:border-zinc-500 cursor-pointer"
                  }`}
                >
                  {state.characterRef ? (
                    <>
                      {state.characterRef.base64 ? (
                        <img
                          src={`data:${state.characterRef.mimeType || "image/png"};base64,${state.characterRef.base64}`}
                          alt="Character Ref"
                          className="w-full h-full object-cover rounded-lg"
                        />
                      ) : (
                        <span className="text-xs font-mono text-indigo-400">ID: {state.characterRef.mediaId.slice(-6)}</span>
                      )}
                      <button
                        type="button"
                        onClick={e => {
                          e.stopPropagation();
                          handleClearReference("character");
                        }}
                        className="absolute top-1.5 right-1.5 bg-black/80 hover:bg-red-600 text-white p-1 rounded-full text-[10px]"
                      >
                        ✕
                      </button>
                    </>
                  ) : (
                    <div className="text-center">
                      <span className="text-2xl text-zinc-500">👤</span>
                      <p className="text-[10px] font-bold text-zinc-400 mt-1">Chọn nhân vật</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Style Ref Slot */}
              <div className="flex flex-col gap-1.5">
                <span className="text-[11px] font-semibold text-zinc-400">Phong cách (Doodle)</span>
                <div
                  onClick={() => !state.styleRef && handleSelectReference("style")}
                  className={`h-28 rounded-xl border-2 border-dashed flex flex-col items-center justify-center p-2 relative transition-all overflow-hidden ${
                    state.styleRef
                      ? "border-pink-500 bg-pink-950/20"
                      : "border-zinc-700 bg-zinc-950/60 hover:border-zinc-500 cursor-pointer"
                  }`}
                >
                  {state.styleRef ? (
                    <>
                      {state.styleRef.base64 ? (
                        <img
                          src={`data:${state.styleRef.mimeType || "image/png"};base64,${state.styleRef.base64}`}
                          alt="Style Ref"
                          className="w-full h-full object-cover rounded-lg"
                        />
                      ) : (
                        <span className="text-xs font-mono text-pink-400">ID: {state.styleRef.mediaId.slice(-6)}</span>
                      )}
                      <button
                        type="button"
                        onClick={e => {
                          e.stopPropagation();
                          handleClearReference("style");
                        }}
                        className="absolute top-1.5 right-1.5 bg-black/80 hover:bg-red-600 text-white p-1 rounded-full text-[10px]"
                      >
                        ✕
                      </button>
                    </>
                  ) : (
                    <div className="text-center">
                      <span className="text-2xl text-zinc-500">🎨</span>
                      <p className="text-[10px] font-bold text-zinc-400 mt-1">Chọn nét vẽ</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Model Summary Info */}
          <div className="mt-auto p-3.5 rounded-xl bg-zinc-950 border border-zinc-800 text-[11px] space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-zinc-500">Model vẽ ảnh:</span>
              <span className="font-bold text-amber-400">Nano Banana 2.1 (0 cr)</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-500">Model video:</span>
              <span className="font-bold text-indigo-400">Omni 1.1 Flash (4-10s)</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-500">Thời lượng tự động:</span>
              <span className="font-mono text-zinc-300">4s | 6s | 8s | 10s</span>
            </div>
          </div>
        </div>

        {/* Right Column: Scene Beats Storyboard Queue & Actions */}
        <div className="flex-1 flex flex-col overflow-hidden bg-zinc-900/20">
          {/* Action Bar */}
          <div className="p-4 border-b border-zinc-800 bg-zinc-900/60 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              <span className="text-sm font-bold text-zinc-200">
                Danh sách phân cảnh ({state.scenes.length})
              </span>
              {state.isProcessing && (
                <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 text-xs">
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                  <span>Đang xử lý...</span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-3">
              {/* Step 1: Batch Keyframe Button */}
              <button
                type="button"
                disabled={state.isProcessing || state.scenes.length === 0}
                onClick={handleGenerateKeyframes}
                className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs shadow-md shadow-amber-600/20 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                <span>🍌</span> Tạo ảnh Keyframes (0 credits)
              </button>

              {/* Step 2: Mode Execution Button */}
              {state.mode === "hybrid_video" ? (
                <button
                  type="button"
                  disabled={state.isProcessing || state.scenes.length === 0}
                  onClick={handleRunOmniVideoChain}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/20 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  <span>🎬</span> Sinh Video Omni 1.1 Flash
                </button>
              ) : (
                <button
                  type="button"
                  disabled={state.isProcessing || state.scenes.length === 0}
                  onClick={handleExportZeroCreditFlipbook}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/20 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  <span>⚡</span> Xuất Storyboard Flipbook (0 cr)
                </button>
              )}
            </div>
          </div>

          {/* Storyboard Grid */}
          <div className="flex-1 p-5 overflow-y-auto">
            {state.scenes.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-zinc-500">
                <span className="text-4xl mb-3">📋</span>
                <p className="text-sm font-semibold">Chưa có phân cảnh nào được tạo.</p>
                <p className="text-xs text-zinc-600 mt-1">Bấm "Tách cảnh tự động qua AI" bên trái để bắt đầu lập Storyboard.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                {state.scenes.map((scene, idx) => (
                  <div
                    key={scene.id}
                    className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 flex gap-4 hover:border-zinc-700 transition-all shadow-sm"
                  >
                    {/* Visual Keyframe Thumbnail */}
                    <div className="w-36 h-24 rounded-lg bg-zinc-950 border border-zinc-800 shrink-0 flex items-center justify-center relative overflow-hidden">
                      {scene.keyframeBase64 ? (
                        <img
                          src={`data:image/png;base64,${scene.keyframeBase64}`}
                          alt={`Scene ${scene.sceneId}`}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="text-center p-2">
                          <span className="text-xl text-zinc-600">🖼️</span>
                          <p className="text-[9px] text-zinc-500 mt-1">Chưa có Keyframe</p>
                        </div>
                      )}

                      {/* Status Overlay Badge */}
                      <span className="absolute bottom-1 right-1 px-1.5 py-0.5 rounded text-[9px] font-bold font-mono bg-black/80 text-zinc-300">
                        {scene.omniDuration}s
                      </span>
                    </div>

                    {/* Content Details */}
                    <div className="flex-1 min-w-0 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-xs font-black text-indigo-400 font-mono">CẢNH #{scene.sceneId}</span>
                          <span
                            className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${
                              scene.status === "VIDEO_READY"
                                ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/30"
                                : scene.status === "IMAGE_READY"
                                ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                                : scene.status === "ERROR"
                                ? "bg-red-500/10 text-red-400 border border-red-500/30"
                                : "bg-zinc-800 text-zinc-400"
                            }`}
                          >
                            {scene.status}
                          </span>
                        </div>

                        <p className="text-xs text-zinc-200 font-medium line-clamp-2 leading-relaxed">
                          "{scene.narration}"
                        </p>
                        <p className="text-[11px] text-zinc-500 font-mono line-clamp-1 mt-1">
                          {scene.visualPrompt}
                        </p>
                      </div>

                      {/* Omni Flash Auto-Duration Selector */}
                      <div className="flex items-center gap-2 mt-2 pt-2 border-t border-zinc-800/60">
                        <span className="text-[10px] text-zinc-500 font-semibold">Thời lượng Omni:</span>
                        <div className="flex gap-1">
                          {([4, 6, 8, 10] as const).map(d => (
                            <button
                              key={d}
                              type="button"
                              onClick={() => {
                                const newScenes = [...state.scenes];
                                newScenes[idx].omniDuration = d;
                                newScenes[idx].durationSeconds = d;
                                persistState({ ...state, scenes: newScenes });
                              }}
                              className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold transition-all ${
                                scene.omniDuration === d
                                  ? "bg-indigo-600 text-white"
                                  : "bg-zinc-800 text-zinc-400 hover:text-white"
                              }`}
                            >
                              {d}s
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Bottom Status Bar */}
          <footer className="px-5 py-2.5 bg-zinc-950 border-t border-zinc-800 flex items-center justify-between text-xs text-zinc-400 shrink-0">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="font-medium text-zinc-300">{state.statusMessage}</span>
            </div>
            <div className="flex items-center gap-3 font-mono text-[11px] text-zinc-500">
              <span>Engine: V2.0.0</span>
              <span>•</span>
              <span>Storage: {STORAGE_KEY}</span>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
