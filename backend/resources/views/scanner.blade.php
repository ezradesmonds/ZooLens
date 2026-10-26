@extends('layouts.app')

@section('title', 'Scanner')

@section('content')
{{-- ===== HERO ===== --}}
<section class="mb-6 sm:mb-8">
    <p class="text-sm font-semibold uppercase tracking-wider text-emerald-600">Smart Animal Scanner</p>
    <h1 class="mt-1 text-3xl font-extrabold tracking-tight text-stone-900 sm:text-4xl">Kenali satwa dari satu foto</h1>
    <p class="mt-2 max-w-2xl text-stone-600">Ambil foto lewat kamera atau unggah dari galeri. ZooLens akan mendeteksi satwa, menampilkan <em>bounding box</em>, tingkat keyakinan, dan fakta edukatifnya.</p>
</section>

<div class="grid gap-6 lg:grid-cols-5">
    {{-- ================= KOLOM INPUT ================= --}}
    <section class="lg:col-span-2">
        <div class="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm sm:p-5">
            {{-- Tabs --}}
            <div class="grid grid-cols-2 gap-1 rounded-xl bg-stone-100 p-1" role="tablist">
                <button id="tabCamera" type="button" role="tab" class="rounded-lg px-3 py-2.5 text-sm font-semibold transition"><i class="fa-solid fa-camera mr-1" aria-hidden="true"></i> Ambil Foto</button>
                <button id="tabUpload" type="button" role="tab" class="rounded-lg px-3 py-2.5 text-sm font-semibold transition"><i class="fa-solid fa-image mr-1" aria-hidden="true"></i> Unggah Galeri</button>
            </div>

            {{-- Panel Kamera --}}
            <div id="panelCamera" class="mt-4">
                <div class="relative aspect-[4/3] overflow-hidden rounded-xl bg-stone-900">
                    <video id="video" class="hidden h-full w-full object-cover" playsinline muted autoplay></video>

                    {{-- Tekan untuk membuka kamera --}}
                    <button id="camPlaceholder" type="button" aria-label="Tekan untuk buka kamera"
                            class="absolute inset-0 grid w-full place-items-center p-6 text-center text-stone-300 transition hover:bg-stone-800 hover:text-white focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-inset focus-visible:ring-emerald-400/60">
                        <span>
                            <i class="fa-solid fa-camera text-5xl" aria-hidden="true"></i>
                            <span class="mt-2 block text-sm font-semibold">Tekan untuk buka kamera</span>
                        </span>
                    </button>

                    {{-- Efek kilat saat jepret --}}
                    <div id="camFlash" class="pointer-events-none absolute inset-0 bg-white opacity-0 transition-opacity duration-150"></div>

                    {{-- Tutup kamera (X, kanan atas) --}}
                    <button id="btnStopCam" type="button" aria-label="Tutup kamera"
                            class="absolute right-3 top-3 hidden h-9 w-9 place-items-center rounded-full bg-black/50 text-white backdrop-blur transition hover:bg-black/70 active:scale-90">
                        <i class="fa-solid fa-xmark" aria-hidden="true"></i>
                    </button>

                    {{-- Tombol jepret --}}
                    <button id="btnCapture" type="button" aria-label="Ambil foto"
                            class="group absolute bottom-4 left-1/2 hidden h-[76px] w-[76px] -translate-x-1/2 place-items-center rounded-full border-4 border-white transition duration-100 active:scale-90">
                        <span class="h-[50px] w-[50px] rounded-full bg-white transition-all duration-100 group-active:h-[42px] group-active:w-[42px] group-active:bg-stone-200"></span>
                    </button>
                </div>
            </div>

            {{-- Panel Upload --}}
            <div id="panelUpload" class="mt-4 hidden">
                <label id="dropzone" for="fileInput"
                       class="flex aspect-[4/3] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-stone-300 bg-stone-50 p-6 text-center transition hover:border-emerald-400 hover:bg-emerald-50/50">
                    <i class="fa-solid fa-image text-5xl text-stone-400" aria-hidden="true"></i>
                    <span class="mt-2 text-sm font-semibold text-stone-700">Klik untuk memilih gambar</span>
                    <span class="mt-1 text-xs text-stone-500">atau seret &amp; lepas di sini · JPG, PNG, WEBP · maks. 8 MB</span>
                </label>
                <input id="fileInput" type="file" accept="image/*" class="sr-only">
            </div>

            {{-- Simulasi (khusus pengembangan) --}}
            <div class="mt-5 rounded-xl border border-dashed border-amber-300 bg-amber-50 p-3">
                <label for="simMode" class="text-xs font-bold uppercase tracking-wide text-amber-700">Mode simulasi (data dummy)</label>
                <select id="simMode" class="mt-1 w-full rounded-lg border border-amber-200 bg-white px-3 py-2 text-sm">
                    <option value="random">Deteksi acak (berhasil)</option>
                    <option value="elephant">Paksa: Gajah</option>
                    <option value="giraffe">Paksa: Jerapah</option>
                    <option value="zebra">Paksa: Zebra</option>
                    <option value="tiger">Paksa: Harimau</option>
                    <option value="rhinoceros">Paksa: Badak</option>
                    <option value="low">Confidence rendah (di bawah threshold)</option>
                    <option value="none">Tidak ada satwa</option>
                </select>
                <p class="mt-1 text-xs text-amber-700">Hapus blok ini &amp; set <code>USE_REAL_API = true</code> saat API FastAPI siap.</p>
            </div>
        </div>

        {{-- Tips --}}
        <div class="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 p-4 text-sm text-emerald-900">
            <p class="font-bold"><i class="fa-solid fa-lightbulb mr-1" aria-hidden="true"></i> Tips foto yang baik</p>
            <ul class="mt-1 list-disc space-y-0.5 pl-5 text-emerald-800">
                <li>Pastikan satwa terlihat jelas dan tidak terlalu tertutup.</li>
                <li>Gunakan pencahayaan yang cukup, hindari gambar buram.</li>
                <li>Satu gambar per pemindaian.</li>
            </ul>
        </div>
    </section>

    {{-- ================= KOLOM HASIL ================= --}}
    <section class="lg:col-span-3">
        {{-- Placeholder awal --}}
        <div id="idleBox" class="grid min-h-[20rem] place-items-center rounded-2xl border border-dashed border-stone-300 bg-white p-8 text-center">
            <div>
                <i class="fa-solid fa-paw text-6xl text-stone-300" aria-hidden="true"></i>
                <h2 class="mt-3 text-lg font-bold text-stone-800">Belum ada foto</h2>
                <p class="mt-1 max-w-sm text-sm text-stone-500">Hasil deteksi beserta Interactive Animal Factsheet akan muncul di sini setelah kamu mengambil atau mengunggah foto.</p>
            </div>
        </div>

        {{-- Error state --}}
        <div id="errorBox" class="hidden rounded-2xl border border-red-200 bg-red-50 p-6 text-center" role="alert">
            <i class="fa-solid fa-triangle-exclamation text-5xl text-red-500" aria-hidden="true"></i>
            <h2 id="errorTitle" class="mt-2 text-lg font-bold text-red-800">Terjadi kendala</h2>
            <p id="errorMsg" class="mx-auto mt-1 max-w-md text-sm text-red-700"></p>
            <div class="mt-4 flex flex-wrap justify-center gap-2">
                <button id="errRetry" type="button" class="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700">Coba lagi</button>
                <button id="errUpload" type="button" class="rounded-lg border border-red-300 bg-white px-4 py-2 text-sm font-semibold text-red-700 hover:bg-red-100">Gunakan Unggah Galeri</button>
            </div>
        </div>

        {{-- Result --}}
        <div id="resultSection" class="hidden">
            <div class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
                <div class="relative bg-stone-900">
                    <canvas id="resultCanvas" class="block h-auto w-full"></canvas>
                    <div id="loadingOverlay" class="absolute inset-0 hidden place-items-center bg-stone-900/60 backdrop-blur-[2px]">
                        <div class="text-center text-white">
                            <svg class="mx-auto h-10 w-10 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/><path d="M4 12a8 8 0 018-8" stroke="currentColor" stroke-width="4" stroke-linecap="round"/></svg>
                            <p class="mt-3 text-sm font-semibold">Menganalisis gambar…</p>
                        </div>
                    </div>
                </div>

                <div class="space-y-3 p-4 sm:p-5">
                    <div id="detList" class="flex flex-wrap gap-2"></div>

                    {{-- Empty (tidak terdeteksi) --}}
                    <div id="emptyBox" class="hidden rounded-xl border border-amber-200 bg-amber-50 p-4">
                        <p class="font-bold text-amber-900"><i class="fa-solid fa-magnifying-glass mr-1" aria-hidden="true"></i> Satwa belum terdeteksi</p>
                        <p id="emptyMsg" class="mt-1 text-sm text-amber-800">Tidak ada satwa dengan tingkat keyakinan yang cukup. Coba foto lebih dekat, pastikan satwa terlihat jelas, atau gunakan pencahayaan yang lebih baik.</p>
                    </div>

                    <div class="flex flex-wrap gap-2">
                        <button id="btnOpenFact" type="button" class="hidden rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-emerald-700"><i class="fa-solid fa-book-open mr-1" aria-hidden="true"></i> Lihat Factsheet</button>
                        <button id="btnReset" type="button" class="rounded-xl border border-stone-300 px-4 py-2.5 text-sm font-semibold text-stone-700 hover:bg-stone-100"><i class="fa-solid fa-rotate-left mr-1" aria-hidden="true"></i> Ulangi Foto</button>
                    </div>
                </div>
            </div>

            <a href="{{ url('/history') }}" class="mt-4 flex items-center justify-center gap-2 rounded-xl border border-stone-300 bg-white px-4 py-3 text-sm font-bold text-stone-700 shadow-sm transition hover:bg-stone-100">
                <i class="fa-solid fa-clock-rotate-left" aria-hidden="true"></i> Buka Riwayat Deteksi
            </a>
        </div>
    </section>
</div>

{{-- ================= MODAL FACTSHEET ================= --}}
@include('partials.factsheet')
@endsection

@push('scripts')
<script>
(() => {
    /* =====================================================================
     * KONFIGURASI
     * ===================================================================== */
    const CONFIG = {
        USE_REAL_API: false,                 // true => kirim gambar ke POST /scan
        SCAN_URL: "{{ url('/scan') }}",
        THRESHOLD: 0.5,                      // confidence minimum
        MAX_W: 1024,                         // lebar maksimum canvas hasil
        MAX_FILE_MB: 8,
    };

    /* Data factsheet ada di partials/factsheet.blade.php (dipakai bersama halaman History). */
    const { FACTS } = window.ZooFactsheet;

    /* =====================================================================
     * ELEMEN
     * ===================================================================== */
    const $ = (id) => document.getElementById(id);
    const el = {
        tabCamera: $('tabCamera'), tabUpload: $('tabUpload'),
        panelCamera: $('panelCamera'), panelUpload: $('panelUpload'),
        video: $('video'), camPlaceholder: $('camPlaceholder'),
        camFlash: $('camFlash'), btnCapture: $('btnCapture'), btnStopCam: $('btnStopCam'),
        dropzone: $('dropzone'), fileInput: $('fileInput'), simMode: $('simMode'),
        idleBox: $('idleBox'), errorBox: $('errorBox'), errorTitle: $('errorTitle'), errorMsg: $('errorMsg'),
        errRetry: $('errRetry'), errUpload: $('errUpload'),
        resultSection: $('resultSection'), canvas: $('resultCanvas'), loading: $('loadingOverlay'),
        detList: $('detList'), emptyBox: $('emptyBox'), emptyMsg: $('emptyMsg'),
        btnOpenFact: $('btnOpenFact'), btnReset: $('btnReset'),
    };

    let stream = null;
    let currentImg = null;
    let currentBlob = null;
    let currentUrl = null;
    let activeTab = 'camera';
    let topDetection = null;
    let resultImage = null;
    let detecting = false;
    let lastErrorAction = null;

    /* =====================================================================
     * UTIL TAMPILAN
     * ===================================================================== */
    const show = (n) => n.classList.remove('hidden');
    const hide = (n) => n.classList.add('hidden');

    function setTab(tab) {
        activeTab = tab;
        const on = 'bg-white text-emerald-700 shadow-sm';
        const off = 'text-stone-600 hover:text-stone-900';
        el.tabCamera.className = 'rounded-lg px-3 py-2.5 text-sm font-semibold transition ' + (tab === 'camera' ? on : off);
        el.tabUpload.className = 'rounded-lg px-3 py-2.5 text-sm font-semibold transition ' + (tab === 'upload' ? on : off);
        el.tabCamera.setAttribute('aria-selected', tab === 'camera');
        el.tabUpload.setAttribute('aria-selected', tab === 'upload');
        el.panelCamera.classList.toggle('hidden', tab !== 'camera');
        el.panelUpload.classList.toggle('hidden', tab !== 'upload');
        if (tab !== 'camera') stopCamera();
    }

    function showError(title, msg, retry) {
        el.errorTitle.textContent = title;
        el.errorMsg.textContent = msg;
        lastErrorAction = retry || null;
        el.errRetry.classList.toggle('hidden', !retry);
        hide(el.idleBox); hide(el.resultSection); show(el.errorBox);
    }
    function clearError() { hide(el.errorBox); }

    /* =====================================================================
     * KAMERA
     * ===================================================================== */
    async function startCamera() {
        if (stream) return;
        clearError();
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            return showError('Kamera tidak tersedia',
                'Browser tidak mendukung akses kamera, atau halaman tidak dibuka lewat HTTPS / localhost. Silakan gunakan Unggah Galeri.');
        }
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } },
                audio: false,
            });
            el.video.srcObject = stream;
            await el.video.play();
            show(el.video); hide(el.camPlaceholder);
            show(el.btnCapture); show(el.btnStopCam);
        } catch (err) {
            stopCamera();
            const name = err && err.name;
            if (name === 'NotAllowedError' || name === 'SecurityError') {
                showError('Izin kamera ditolak',
                    'Aktifkan izin kamera untuk situs ini di pengaturan browser (ikon gembok di address bar), lalu coba lagi. Atau gunakan Unggah Galeri.', startCamera);
            } else if (name === 'NotFoundError' || name === 'OverconstrainedError') {
                showError('Kamera tidak ditemukan', 'Perangkat ini tidak memiliki kamera yang bisa digunakan. Silakan unggah gambar dari galeri.');
            } else if (name === 'NotReadableError') {
                showError('Kamera sedang dipakai', 'Tutup aplikasi lain yang memakai kamera, lalu coba lagi.', startCamera);
            } else {
                showError('Gagal membuka kamera', 'Terjadi kesalahan saat mengakses kamera. Silakan coba lagi atau gunakan Unggah Galeri.', startCamera);
            }
        }
    }

    function stopCamera() {
        if (stream) stream.getTracks().forEach((t) => t.stop());
        stream = null;
        el.video.srcObject = null;
        hide(el.video); show(el.camPlaceholder);
        hide(el.btnCapture); hide(el.btnStopCam);
    }

    function capture() {
        if (!stream || !el.video.videoWidth || detecting) return;
        const c = document.createElement('canvas');
        c.width = el.video.videoWidth;
        c.height = el.video.videoHeight;
        c.getContext('2d').drawImage(el.video, 0, 0, c.width, c.height);
        el.camFlash.classList.replace('opacity-0', 'opacity-100');
        setTimeout(() => el.camFlash.classList.replace('opacity-100', 'opacity-0'), 120);
        c.toBlob((blob) => {
            if (!blob) return showError('Gagal mengambil foto', 'Foto tidak berhasil diproses. Silakan coba lagi.', startCamera);
            loadBlob(blob);
        }, 'image/jpeg', 0.9);
    }

    /* =====================================================================
     * UNGGAH GALERI
     * ===================================================================== */
    function handleFile(file) {
        if (!file) return;
        if (!file.type.startsWith('image/')) {
            return showError('Berkas tidak valid', 'Hanya file gambar (JPG, PNG, WEBP) yang didukung.');
        }
        if (file.size > CONFIG.MAX_FILE_MB * 1024 * 1024) {
            return showError('Ukuran terlalu besar', 'Ukuran gambar maksimal ' + CONFIG.MAX_FILE_MB + ' MB.');
        }
        loadBlob(file);
    }

    /* =====================================================================
     * LOAD GAMBAR -> DETEKSI
     * ===================================================================== */
    function loadBlob(blob) {
        if (currentUrl) URL.revokeObjectURL(currentUrl);
        currentUrl = URL.createObjectURL(blob);
        currentBlob = blob;
        const img = new Image();
        img.onload = () => { currentImg = img; runDetection(); };
        img.onerror = () => showError('Gambar tidak dapat dibaca', 'File gambar rusak atau formatnya tidak didukung.');
        img.src = currentUrl;
    }

    function sizeCanvas() {
        const scale = Math.min(1, CONFIG.MAX_W / currentImg.naturalWidth);
        el.canvas.width = Math.round(currentImg.naturalWidth * scale);
        el.canvas.height = Math.round(currentImg.naturalHeight * scale);
    }

    function drawBase() {
        const ctx = el.canvas.getContext('2d');
        ctx.drawImage(currentImg, 0, 0, el.canvas.width, el.canvas.height);
    }

    function drawOverlay(dets) {
        const ctx = el.canvas.getContext('2d');
        const W = el.canvas.width, H = el.canvas.height;
        const lw = Math.max(3, W / 200);
        const fs = Math.max(14, Math.round(W / 38));
        ctx.lineJoin = 'round';
        ctx.font = '700 ' + fs + 'px Inter, system-ui, sans-serif';
        ctx.textBaseline = 'middle';

        dets.forEach((d) => {
            const f = FACTS[d.class];
            const x = d.bbox.x * W, y = d.bbox.y * H, w = d.bbox.width * W, h = d.bbox.height * H;

            ctx.strokeStyle = f.color;
            ctx.lineWidth = lw;
            ctx.strokeRect(x, y, w, h);

            const label = f.name + ' · ' + Math.round(d.confidence * 100) + '%';
            const padX = fs * 0.6, boxH = fs * 1.7;
            const boxW = ctx.measureText(label).width + padX * 2;
            let ly = y - boxH;
            if (ly < 0) ly = y;                       // taruh di dalam bila mepet atas
            const lx = Math.min(Math.max(0, x - lw / 2), W - boxW);

            ctx.fillStyle = f.color;
            ctx.fillRect(lx, ly, boxW, boxH);
            ctx.fillStyle = '#ffffff';
            ctx.fillText(label, lx + padX, ly + boxH / 2 + 1);
        });
    }

    function setLoading(on) {
        el.loading.classList.toggle('hidden', on === false);
        el.loading.classList.toggle('grid', on === true);
    }

    async function runDetection() {
        detecting = true;
        clearError(); hide(el.idleBox); show(el.resultSection);
        hide(el.emptyBox); hide(el.btnOpenFact); el.detList.innerHTML = '';
        sizeCanvas(); drawBase(); setLoading(true);
        topDetection = null;

        try {
            const data = CONFIG.USE_REAL_API ? await detectViaApi(currentBlob) : await detectDummy();
            const dets = (data.detections || [])
                .filter((d) => d.confidence >= CONFIG.THRESHOLD && FACTS[d.class])
                .sort((a, b) => b.confidence - a.confidence);

            drawBase();
            drawOverlay(dets);
            resultImage = el.canvas.toDataURL('image/jpeg', 0.85);

            if (!dets.length) {
                const best = (data.detections || [])[0];
                el.emptyMsg.textContent = best
                    ? 'Model menemukan objek, tetapi keyakinannya (' + Math.round(best.confidence * 100) + '%) di bawah batas minimum ' + Math.round(CONFIG.THRESHOLD * 100) + '%. Coba foto lebih dekat atau dengan pencahayaan lebih baik.'
                    : 'Tidak ada satwa yang terdeteksi pada gambar ini. Pastikan satwa terlihat jelas (bukan hanya sebagian kecil tubuhnya), lalu coba lagi.';
                show(el.emptyBox);
                return;
            }

            dets.forEach((d) => {
                const f = FACTS[d.class];
                const chip = document.createElement('span');
                chip.className = 'inline-flex items-center gap-1.5 rounded-full bg-stone-100 px-3 py-1.5 text-sm font-semibold text-stone-700';
                chip.innerHTML = '<i class="fa-solid fa-paw" style="color:' + f.color + '" aria-hidden="true"></i> ' + f.name + ' · ' + Math.round(d.confidence * 100) + '%';
                el.detList.appendChild(chip);
            });

            topDetection = dets[0];
            show(el.btnOpenFact);
            openFactsheet();
        } catch (err) {
            showError('Gagal memproses gambar', (err && err.message) || 'Terjadi kesalahan saat mendeteksi satwa.', runDetection);
        } finally {
            detecting = false;
            setLoading(false);
        }
    }

    /* =====================================================================
     * DETEKSI: DUMMY & API ASLI
     *
     * Format JSON yang diharapkan (koordinat bbox ter-normalisasi 0..1):
     * { "detections": [ { "class": "elephant", "confidence": 0.92,
     *     "bbox": { "x": 0.2, "y": 0.25, "width": 0.5, "height": 0.6 } } ] }
     * Jika FastAPI mengembalikan piksel (x1,y1,x2,y2), konversi dulu di sini.
     * ===================================================================== */
    function rand(min, max) { return min + Math.random() * (max - min); }

    function detectDummy() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const mode = el.simMode.value;
                if (mode === 'none') return resolve({ detections: [] });
                const keys = Object.keys(FACTS);
                const cls = (mode === 'random' || mode === 'low') ? keys[Math.floor(Math.random() * keys.length)] : mode;
                const w = rand(0.4, 0.6), h = rand(0.45, 0.6);
                resolve({
                    detections: [{
                        class: cls,
                        confidence: mode === 'low' ? rand(0.25, 0.45) : rand(0.78, 0.97),
                        bbox: { x: rand(0.05, 0.95 - w), y: rand(0.1, 0.9 - h), width: w, height: h },
                    }],
                });
            }, 900);
        });
    }

    async function detectViaApi(blob) {
        const fd = new FormData();
        fd.append('image', blob, 'capture.jpg');
        const res = await fetch(CONFIG.SCAN_URL, {
            method: 'POST',
            headers: {
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
                'Accept': 'application/json',
            },
            body: fd,
        });
        if (!res.ok) throw new Error('Server mengembalikan status ' + res.status + '. Coba lagi beberapa saat.');
        return res.json();
    }

    /* =====================================================================
     * FACTSHEET (modal ada di partial bersama)
     * ===================================================================== */
    function openFactsheet() {
        if (!topDetection) return;
        window.ZooFactsheet.open({ class: topDetection.class, confidence: topDetection.confidence, image: resultImage });
    }

    /* =====================================================================
     * RESET
     * ===================================================================== */
    function resetAll() {
        window.ZooFactsheet.close();
        currentImg = null; currentBlob = null; topDetection = null; resultImage = null;
        if (currentUrl) { URL.revokeObjectURL(currentUrl); currentUrl = null; }
        el.fileInput.value = '';
        hide(el.resultSection); hide(el.errorBox); show(el.idleBox);
        if (activeTab === 'camera') startCamera();
    }

    /* =====================================================================
     * EVENT
     * ===================================================================== */
    el.tabCamera.addEventListener('click', () => setTab('camera'));
    el.tabUpload.addEventListener('click', () => setTab('upload'));
    el.camPlaceholder.addEventListener('click', startCamera);
    el.btnStopCam.addEventListener('click', stopCamera);
    el.btnCapture.addEventListener('click', capture);
    el.btnReset.addEventListener('click', resetAll);
    el.btnOpenFact.addEventListener('click', openFactsheet);

    el.fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    ['dragenter', 'dragover'].forEach((ev) => el.dropzone.addEventListener(ev, (e) => {
        e.preventDefault(); el.dropzone.classList.add('border-emerald-500', 'bg-emerald-50');
    }));
    ['dragleave', 'drop'].forEach((ev) => el.dropzone.addEventListener(ev, (e) => {
        e.preventDefault(); el.dropzone.classList.remove('border-emerald-500', 'bg-emerald-50');
    }));
    el.dropzone.addEventListener('drop', (e) => handleFile(e.dataTransfer.files[0]));

    el.errRetry.addEventListener('click', () => { if (lastErrorAction) { clearError(); lastErrorAction(); } });
    el.errUpload.addEventListener('click', () => { clearError(); setTab('upload'); show(el.idleBox); });

    window.addEventListener('beforeunload', stopCamera);

    setTab('camera');
})();
</script>
@endpush