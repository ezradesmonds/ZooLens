@extends('layouts.app')

@section('title', 'Riwayat Deteksi')

@section('content')
@php
    /*
     * Jika HistoryController mengirim $histories, view memakainya.
     * Field yang dibaca: animal, name, confidence (0..1), detected_at, fact, image_url (opsional).
     * Jika tidak ada, tampil data DUMMY di bawah ini.
     */
    $histories = $histories ?? [
        ['animal' => 'zebra',      'name' => 'Zebra',   'confidence' => 0.94, 'detected_at' => '2026-10-15 09:41:00', 'fact' => 'Pola belang setiap zebra unik, seperti sidik jari manusia.'],
        ['animal' => 'giraffe',    'name' => 'Jerapah', 'confidence' => 0.88, 'detected_at' => '2026-10-13 14:05:00', 'fact' => 'Jerapah hanya tidur sekitar 30 menit hingga 2 jam per hari.'],
        ['animal' => 'elephant',   'name' => 'Gajah',   'confidence' => 0.91, 'detected_at' => '2026-10-12 10:24:00', 'fact' => 'Gajah adalah mamalia darat terbesar dan punya ingatan yang sangat kuat.'],
        ['animal' => 'elephant',   'name' => 'Gajah',   'confidence' => 0.73, 'detected_at' => '2026-10-12 10:19:00', 'fact' => 'Belalai gajah memiliki lebih dari 40.000 otot.'],
    ];

    $gradients = [
        'elephant'   => 'from-sky-100 to-sky-200',
        'giraffe'    => 'from-amber-100 to-orange-200',
        'zebra'      => 'from-indigo-100 to-violet-200',
        'tiger'      => 'from-orange-100 to-red-200',
        'rhinoceros' => 'from-emerald-100 to-teal-200',
    ];
@endphp

<section class="mb-6 flex flex-col justify-between gap-3 sm:mb-8 sm:flex-row sm:items-end">
    <div>
        <p class="text-sm font-semibold uppercase tracking-wider text-emerald-600">Riwayat</p>
        <h1 class="mt-1 text-3xl font-extrabold tracking-tight text-stone-900 sm:text-4xl">Riwayat Deteksi</h1>
        <p class="mt-2 text-stone-600">Satwa yang pernah kamu pindai beserta waktu dan fakta singkatnya.</p>
    </div>
    @if (count($histories) > 0)
        <span class="inline-flex w-fit items-center rounded-full bg-emerald-50 px-4 py-2 text-sm font-bold text-emerald-700">{{ count($histories) }} deteksi</span>
    @endif
</section>

@if (count($histories) === 0)
    <div class="grid place-items-center rounded-2xl border border-dashed border-stone-300 bg-white p-10 text-center">
        <i class="fa-solid fa-binoculars text-6xl text-stone-300" aria-hidden="true"></i>
        <h2 class="mt-3 text-lg font-bold text-stone-800">Belum ada riwayat</h2>
        <p class="mt-1 max-w-sm text-sm text-stone-500">Pindai satwa pertamamu dan hasilnya akan tersimpan di sini.</p>
        <a href="{{ url('/') }}" class="mt-4 rounded-xl bg-emerald-600 px-5 py-3 text-sm font-bold text-white hover:bg-emerald-700"><i class="fa-solid fa-camera mr-1" aria-hidden="true"></i> Mulai Pindai</a>
    </div>
@else
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        @foreach ($histories as $h)
            @php
                $when = \Carbon\Carbon::parse($h['detected_at'])->locale('id');
                $pct  = (int) round(($h['confidence'] ?? 0) * 100);
                $grad = $gradients[$h['animal'] ?? ''] ?? 'from-stone-100 to-stone-200';
            @endphp
            <article data-history-index="{{ $loop->index }}" role="button" tabindex="0" aria-label="Lihat factsheet {{ $h['name'] }}"
                     class="flex cursor-pointer overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md focus:outline-none focus-visible:ring-4 focus-visible:ring-emerald-200 sm:flex-col">
                {{-- Thumbnail --}}
                <div class="relative grid w-28 shrink-0 place-items-center bg-gradient-to-br {{ $grad }} sm:h-40 sm:w-full">
                    @if (!empty($h['image_url']))
                        <img src="{{ $h['image_url'] }}" alt="Foto {{ $h['name'] }}" class="absolute inset-0 h-full w-full object-cover" loading="lazy">
                    @else
                        <i class="fa-solid fa-paw text-5xl text-stone-500/70 sm:text-6xl" aria-hidden="true"></i>
                    @endif
                    <span class="absolute left-2 top-2 rounded-full bg-white/90 px-2 py-0.5 text-[11px] font-extrabold text-emerald-700 shadow-sm">{{ $pct }}%</span>
                </div>

                {{-- Info --}}
                <div class="flex min-w-0 flex-1 flex-col p-4">
                    <div class="flex items-start justify-between gap-2">
                        <h2 class="truncate text-lg font-extrabold text-stone-900">{{ $h['name'] }}</h2>
                    </div>
                    <p class="mt-0.5 text-xs font-medium text-stone-500">
                        <i class="fa-solid fa-calendar-days mr-1" aria-hidden="true"></i> {{ $when->translatedFormat('d F Y') }} · {{ $when->format('H:i') }} WIB
                        <span class="text-stone-400">({{ $when->diffForHumans() }})</span>
                    </p>
                    <p class="mt-3 rounded-lg bg-stone-50 p-2.5 text-sm leading-snug text-stone-600">
                        <span class="font-semibold text-stone-700"><i class="fa-solid fa-lightbulb text-amber-500 mr-1" aria-hidden="true"></i> Fakta:</span> {{ $h['fact'] }}
                    </p>
                    <p class="mt-auto pt-3 text-xs font-bold text-emerald-700">Ketuk untuk lihat factsheet <i class="fa-solid fa-arrow-right ml-0.5" aria-hidden="true"></i></p>
                </div>
            </article>
        @endforeach
    </div>
@endif

@include('partials.factsheet')
@endsection

@push('scripts')
<div id="historyData" class="hidden" data-items="{{ json_encode(collect($histories)->values()) }}"></div>
<script>
(function () {
    var items = JSON.parse(document.getElementById('historyData').dataset.items);

    function openItem(card) {
        var h = items[card.dataset.historyIndex];
        if (!h) return;
        window.ZooFactsheet.open({ class: h.animal, confidence: h.confidence, image: h.image_url || null });
    }

    document.querySelectorAll('[data-history-index]').forEach(function (card) {
        card.addEventListener('click', function () { openItem(card); });
        card.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openItem(card); }
        });
    });
})();
</script>
@endpush