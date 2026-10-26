{{-- Modal Factsheet (dipakai di Scanner & History). Panggil: ZooFactsheet.open({class, confidence, image}) --}}
<div id="factModal" class="fixed inset-0 z-50 hidden" role="dialog" aria-modal="true" aria-labelledby="factTitle">
    <div id="factBackdrop" class="absolute inset-0 bg-stone-900/60 backdrop-blur-sm"></div>
    <div class="absolute inset-x-0 bottom-0 max-h-[92vh] overflow-y-auto rounded-t-3xl bg-white shadow-2xl sm:inset-0 sm:m-auto sm:h-fit sm:max-w-lg sm:rounded-3xl">
        <div class="relative bg-gradient-to-br from-emerald-600 to-emerald-800 px-6 pb-6 pt-7 text-white">
            <button id="factClose" type="button" aria-label="Tutup" class="absolute right-4 top-4 grid h-9 w-9 place-items-center rounded-full bg-white/15 text-xl hover:bg-white/25">×</button>
            <div class="flex items-center gap-4">
                <div id="factEmoji" class="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-white/15 text-4xl"><i class="fa-solid fa-paw" aria-hidden="true"></i></div>
                <div class="min-w-0">
                    <p class="text-xs font-semibold uppercase tracking-wider text-emerald-100">Interactive Animal Factsheet</p>
                    <h2 id="factTitle" class="truncate text-2xl font-extrabold">Gajah</h2>
                    <p id="factSci" class="truncate text-sm italic text-emerald-100">Loxodonta africana</p>
                </div>
            </div>
            <div class="mt-4">
                <div class="flex items-center justify-between text-xs font-semibold text-emerald-100">
                    <span>Tingkat keyakinan model</span><span id="factConfText">0%</span>
                </div>
                <div class="mt-1 h-2 overflow-hidden rounded-full bg-white/20"><div id="factConfBar" class="h-full rounded-full bg-amber-300 transition-all duration-700" style="width:0%"></div></div>
            </div>
        </div>

        <div id="factPhotoWrap" class="hidden bg-stone-900">
            <img id="factPhoto" alt="Foto hasil pindai" class="mx-auto block max-h-64 w-full object-contain">
        </div>

        <div class="space-y-4 p-6">
            <div class="flex items-center justify-between gap-3 rounded-xl border border-stone-200 p-3">
                <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-stone-500">Status Konservasi IUCN</p>
                    <p id="factIucnLabel" class="font-bold text-stone-800">Endangered</p>
                </div>
                <span id="factIucnBadge" class="rounded-full px-3 py-1.5 text-sm font-extrabold">EN</span>
            </div>

            <dl class="space-y-3 text-sm">
                <div class="rounded-xl bg-stone-50 p-3">
                    <dt class="font-bold text-stone-700"><i class="fa-solid fa-earth-asia mr-1" aria-hidden="true"></i> Habitat</dt>
                    <dd id="factHabitat" class="mt-0.5 text-stone-600"></dd>
                </div>
                <div class="rounded-xl bg-stone-50 p-3">
                    <dt class="font-bold text-stone-700"><i class="fa-solid fa-leaf mr-1" aria-hidden="true"></i> Pola Makan</dt>
                    <dd id="factDiet" class="mt-0.5 text-stone-600"></dd>
                </div>
            </dl>

            <div class="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                <i class="fa-solid fa-medal mr-1" aria-hidden="true"></i> <span class="font-semibold">Lencana <span id="factBadgeName">Gajah</span> terbuka!</span>
                <a href="{{ url('/safari') }}" class="ml-1 font-bold underline">Lihat koleksi Safari <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
            </div>

            <p class="text-xs text-stone-400">Data factsheet bersifat dummy. Verifikasi status konservasi pada IUCN Red List sebelum rilis.</p>
            <button id="factDone" type="button" class="w-full rounded-xl bg-stone-900 px-4 py-3 text-sm font-bold text-white hover:bg-stone-700">Tutup</button>
        </div>
    </div>
</div>

@push('scripts')
<script>
window.ZooFactsheet = (() => {
    /* Factsheet dummy. Kunci = nama kelas dari model (YOLO). */
    const FACTS = {
        elephant: { name: 'Gajah', sci: 'Loxodonta africana', color: '#10b981',
            habitat: 'Sabana, hutan, dan padang rumput di Afrika Sub-Sahara; gajah Asia hidup di hutan Asia Selatan & Tenggara.',
            diet: 'Herbivora: rumput, daun, ranting, kulit kayu, dan buah. Dapat makan hingga ±150 kg per hari.', iucn: 'EN' },
        giraffe: { name: 'Jerapah', sci: 'Giraffa camelopardalis', color: '#f59e0b',
            habitat: 'Sabana dan hutan terbuka di Afrika bagian timur dan selatan.',
            diet: 'Herbivora: daun akasia, tunas, dan buah. Lehernya yang panjang menjangkau dedaunan tinggi.', iucn: 'VU' },
        zebra: { name: 'Zebra', sci: 'Equus quagga', color: '#6366f1',
            habitat: 'Padang rumput dan sabana di Afrika timur dan selatan.',
            diet: 'Herbivora: terutama rumput, kadang daun dan semak.', iucn: 'NT' },
        tiger: { name: 'Harimau', sci: 'Panthera tigris', color: '#ef4444',
            habitat: 'Hutan tropis, hutan bakau, dan padang rumput di Asia.',
            diet: 'Karnivora: rusa, babi hutan, dan mamalia besar lain.', iucn: 'EN' },
        rhinoceros: { name: 'Badak', sci: 'Diceros bicornis', color: '#0ea5e9',
            habitat: 'Sabana dan semak belukar di Afrika; spesies Asia hidup di hutan dan padang rumput basah.',
            diet: 'Herbivora: rumput, daun, ranting, dan semak.', iucn: 'CR' },
    };

    const IUCN = {
        LC: { label: 'Least Concern',       cls: 'bg-green-100 text-green-800 ring-1 ring-green-300' },
        NT: { label: 'Near Threatened',     cls: 'bg-lime-100 text-lime-800 ring-1 ring-lime-300' },
        VU: { label: 'Vulnerable',          cls: 'bg-yellow-100 text-yellow-800 ring-1 ring-yellow-300' },
        EN: { label: 'Endangered',          cls: 'bg-orange-100 text-orange-800 ring-1 ring-orange-300' },
        CR: { label: 'Critically Endangered', cls: 'bg-red-100 text-red-800 ring-1 ring-red-300' },
    };

    const $ = (id) => document.getElementById(id);
    const modal = $('factModal');

    function render(d) {
        const f = FACTS[d.class];
        const iucn = IUCN[f.iucn];
        $('factTitle').textContent = f.name;
        $('factSci').textContent = f.sci;
        $('factHabitat').textContent = f.habitat;
        $('factDiet').textContent = f.diet;
        $('factBadgeName').textContent = f.name;
        $('factIucnLabel').textContent = iucn.label;
        const badge = $('factIucnBadge');
        badge.textContent = f.iucn;
        badge.className = 'rounded-full px-3 py-1.5 text-sm font-extrabold ' + iucn.cls;

        const wrap = $('factPhotoWrap');
        if (d.image) { $('factPhoto').src = d.image; wrap.classList.remove('hidden'); }
        else { $('factPhoto').removeAttribute('src'); wrap.classList.add('hidden'); }

        const pct = Math.round((d.confidence || 0) * 100);
        $('factConfText').textContent = pct + '%';
        $('factConfBar').style.width = '0%';
        requestAnimationFrame(() => requestAnimationFrame(() => { $('factConfBar').style.width = pct + '%'; }));
    }

    function open(d) {
        if (!d || !FACTS[d.class]) return;
        render(d);
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        modal.querySelector('.overflow-y-auto').scrollTop = 0;
    }
    function close() { modal.classList.add('hidden'); document.body.style.overflow = ''; }

    $('factClose').addEventListener('click', close);
    $('factDone').addEventListener('click', close);
    $('factBackdrop').addEventListener('click', close);
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });

    return { FACTS, IUCN, open, close };
})();
</script>
@endpush