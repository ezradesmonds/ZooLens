@extends('layouts.app')

@section('title', 'Zoo Digital Safari')

@section('content')
@php
    // Fallback agar view tetap bisa dibuka walau controller belum mengirim data.
    $animals  = $animals  ?? [];
    $total    = $total    ?? count($animals);
    $unlocked = $unlocked ?? count(array_filter($animals, fn ($a) => !empty($a['unlocked'])));
    $percent  = $percent  ?? ($total > 0 ? (int) round($unlocked / $total * 100) : 0);

    $radius = 52;
    $circ   = 2 * M_PI * $radius;
    $offset = $circ * (1 - $percent / 100);

    $palette = [
        'elephant'   => ['from-sky-400 to-sky-600',      'ring-sky-200'],
        'giraffe'    => ['from-amber-400 to-orange-500', 'ring-amber-200'],
        'zebra'      => ['from-indigo-400 to-violet-600','ring-indigo-200'],
        'tiger'      => ['from-orange-500 to-red-600',   'ring-orange-200'],
        'rhinoceros' => ['from-emerald-400 to-teal-600', 'ring-emerald-200'],
    ];
@endphp

{{-- ===== HEADER PROGRES ===== --}}
<section class="overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-600 to-emerald-800 p-6 text-white shadow-lg sm:p-8">
    <div class="flex flex-col items-center gap-6 sm:flex-row sm:justify-between">
        <div class="text-center sm:text-left">
            <p class="text-sm font-semibold uppercase tracking-wider text-emerald-100">Zoo Digital Safari</p>
            <h1 class="mt-1 text-3xl font-extrabold tracking-tight sm:text-4xl">Koleksi Lencana Safari</h1>
            <p class="mt-2 max-w-md text-emerald-50">Temukan dan pindai semua satwa di kebun binatang untuk membuka lencana digitalmu.</p>

            <div class="mt-4 inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-2 text-sm font-bold">
                <i class="fa-solid fa-star text-amber-300" aria-hidden="true"></i> {{ $unlocked }}/{{ $total }} Satwa ditemukan
            </div>

            <div class="mt-4 max-w-xs sm:max-w-sm">
                <div class="h-2.5 overflow-hidden rounded-full bg-white/20">
                    <div class="h-full rounded-full bg-amber-300 transition-all duration-700" @style(["width: {$percent}%"])></div>
                </div>
            </div>
        </div>

        <div class="relative grid h-36 w-36 shrink-0 place-items-center">
            <svg class="-rotate-90" width="144" height="144" viewBox="0 0 120 120" aria-hidden="true">
                <circle cx="60" cy="60" r="{{ $radius }}" fill="none" stroke="rgba(255,255,255,.2)" stroke-width="10"/>
                <circle cx="60" cy="60" r="{{ $radius }}" fill="none" stroke="#fcd34d" stroke-width="10" stroke-linecap="round"
                        stroke-dasharray="{{ $circ }}" stroke-dashoffset="{{ $offset }}"/>
            </svg>
            <div class="absolute text-center">
                <div class="text-4xl font-extrabold leading-none">{{ $percent }}<span class="text-xl">%</span></div>
                <div class="mt-1 text-xs font-semibold uppercase tracking-wide text-emerald-100">Terbuka</div>
            </div>
        </div>
    </div>
</section>

{{-- ===== GRID LENCANA ===== --}}
<section class="mt-8">
    <h2 class="text-lg font-bold text-stone-900">Katalog Lencana</h2>

    @if (count($animals) === 0)
        <div class="mt-4 rounded-2xl border border-dashed border-stone-300 bg-white p-10 text-center text-stone-500">
            Belum ada data lencana.
        </div>
    @else
        <div class="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            @foreach ($animals as $a)
                @php
                    $isOpen = !empty($a['unlocked']);
                    [$grad, $ring] = $palette[$a['key']] ?? ['from-emerald-400 to-emerald-600', 'ring-emerald-200'];
                @endphp

                @if ($isOpen)
                    {{-- Badge TERBUKA --}}
                    <article class="group flex flex-col items-center rounded-2xl border border-stone-200 bg-white p-4 text-center shadow-sm transition hover:-translate-y-1 hover:shadow-md">
                        <div class="relative grid h-24 w-24 place-items-center rounded-full bg-gradient-to-br {{ $grad }} text-5xl shadow-inner ring-4 {{ $ring }}">
                            <i class="fa-solid fa-paw drop-shadow" aria-hidden="true"></i>
                            <span class="absolute -bottom-1 -right-1 grid h-8 w-8 place-items-center rounded-full bg-emerald-500 text-sm font-bold text-white ring-2 ring-white"><i class="fa-solid fa-check" aria-hidden="true"></i></span>
                        </div>
                        <h3 class="mt-3 font-extrabold text-stone-900">{{ $a['name'] }}</h3>
                        <p class="text-xs text-stone-500">{{ $a['en'] }}</p>
                        <p class="mt-2 rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold text-emerald-700">
                            Didapat {{ \Carbon\Carbon::parse($a['unlocked_at'])->locale('id')->translatedFormat('d M Y') }}
                        </p>
                    </article>
                @else
                    {{-- Badge TERKUNCI --}}
                    <article class="flex flex-col items-center rounded-2xl border border-dashed border-stone-300 bg-stone-100/70 p-4 text-center" aria-label="{{ $a['name'] }} terkunci">
                        <div class="relative grid h-24 w-24 place-items-center rounded-full bg-stone-200 ring-4 ring-stone-100">
                            <i class="fa-solid fa-paw text-stone-400 opacity-60" aria-hidden="true"></i>
                            <span class="absolute inset-0 grid place-items-center rounded-full bg-stone-400/30">
                                <svg class="h-9 w-9 text-stone-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2a5 5 0 00-5 5v3H6a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2v-8a2 2 0 00-2-2h-1V7a5 5 0 00-5-5zm-3 8V7a3 3 0 116 0v3H9z"/></svg>
                            </span>
                        </div>
                        <h3 class="mt-3 font-extrabold text-stone-500">{{ $a['name'] }}</h3>
                        <p class="text-xs text-stone-400">{{ $a['en'] }}</p>
                        <p class="mt-2 rounded-full bg-stone-200 px-2.5 py-1 text-[11px] font-semibold text-stone-500"><i class="fa-solid fa-lock mr-1" aria-hidden="true"></i> Belum ditemukan</p>
                    </article>
                @endif
            @endforeach
        </div>
    @endif
</section>

{{-- ===== CTA ===== --}}
<section class="mt-8 flex flex-col items-center justify-between gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-center sm:flex-row sm:text-left">
    <div>
        <p class="font-bold text-amber-900">
            @if ($unlocked >= $total && $total > 0)
                <i class="fa-solid fa-trophy mr-1" aria-hidden="true"></i> Selamat! Semua lencana sudah terkumpul.
            @else
                Masih ada {{ max(0, $total - $unlocked) }} satwa lagi yang menunggu!
            @endif
        </p>
        <p class="text-sm text-amber-800">Pindai satwa di sekitarmu untuk membuka lencana berikutnya.</p>
    </div>
    <a href="{{ url('/') }}" class="shrink-0 rounded-xl bg-amber-500 px-5 py-3 text-sm font-bold text-white shadow-sm hover:bg-amber-600"><i class="fa-solid fa-camera mr-1" aria-hidden="true"></i> Mulai Pindai</a>
</section>
@endsection