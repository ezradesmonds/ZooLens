<!DOCTYPE html>
<html lang="id" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'ZooLens') · ZooLens</title>

    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'] },
                },
            },
        };
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
        body { font-family: 'Inter', ui-sans-serif, system-ui, sans-serif; }
        .safe-bottom { padding-bottom: env(safe-area-inset-bottom); }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    @stack('styles')
</head>
<body class="min-h-screen flex flex-col bg-stone-50 text-stone-800 antialiased">

@php
    $navItems = [
        ['label' => 'Scanner', 'url' => url('/'),        'active' => request()->is('/'),         'icon' => 'camera'],
        ['label' => 'Safari',  'url' => url('/safari'),  'active' => request()->is('safari*'),   'icon' => 'medal'],
        ['label' => 'History', 'url' => url('/history'), 'active' => request()->is('history*'),  'icon' => 'clock-rotate-left'],
    ];
@endphp

{{-- ===== NAVBAR ===== --}}
<header class="sticky top-0 z-40 border-b border-emerald-900/10 bg-white/90 backdrop-blur">
    <nav class="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <a href="{{ url('/') }}" class="flex items-center gap-2 font-extrabold tracking-tight text-emerald-800">
            <span class="grid h-9 w-9 place-items-center rounded-xl bg-emerald-600 text-lg text-white shadow-sm"><i class="fa-solid fa-paw" aria-hidden="true"></i></span>
            <span class="text-xl">Zoo<span class="text-amber-500">Lens</span></span>
        </a>

        {{-- Desktop menu --}}
        <div class="hidden items-center gap-1 md:flex">
            @foreach ($navItems as $item)
                <a href="{{ $item['url'] }}"
                   class="rounded-lg px-4 py-2 text-sm font-semibold transition
                          {{ $item['active'] ? 'bg-emerald-50 text-emerald-700' : 'text-stone-600 hover:bg-stone-100 hover:text-stone-900' }}">
                    {{ $item['label'] }}
                </a>
            @endforeach

            <div class="ml-3 flex items-center gap-3 border-l border-stone-200 pl-4">
                @auth
                    <span class="max-w-[10rem] truncate text-sm text-stone-500">Hai, {{ auth()->user()->name }}</span>
                    <form method="POST" action="{{ url('/logout') }}">
                        @csrf
                        <button type="submit"
                                class="rounded-lg border border-stone-300 px-4 py-2 text-sm font-semibold text-stone-700 transition hover:bg-stone-100">
                            Logout
                        </button>
                    </form>
                @else
                    <a href="{{ url('/login') }}"
                       class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700">
                        Login
                    </a>
                @endauth
            </div>
        </div>

        {{-- Mobile toggle --}}
        <button id="navToggle" type="button" aria-label="Buka menu" aria-expanded="false"
                class="grid h-10 w-10 place-items-center rounded-lg text-stone-700 hover:bg-stone-100 md:hidden">
            <svg id="iconOpen" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 7h16M4 12h16M4 17h16"/></svg>
            <svg id="iconClose" class="hidden h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M6 6l12 12M18 6L6 18"/></svg>
        </button>
    </nav>

    {{-- Mobile menu --}}
    <div id="mobileMenu" class="hidden border-t border-stone-200 bg-white md:hidden">
        <div class="mx-auto max-w-6xl space-y-1 px-4 py-3">
            @foreach ($navItems as $item)
                <a href="{{ $item['url'] }}"
                   class="flex items-center gap-3 rounded-lg px-3 py-3 text-base font-semibold
                          {{ $item['active'] ? 'bg-emerald-50 text-emerald-700' : 'text-stone-700 hover:bg-stone-100' }}">
                    <i class="fa-solid fa-{{ $item['icon'] }} w-5 text-center text-emerald-600" aria-hidden="true"></i> {{ $item['label'] }}
                </a>
            @endforeach
            <div class="pt-2">
                @auth
                    <form method="POST" action="{{ url('/logout') }}">
                        @csrf
                        <button type="submit" class="w-full rounded-lg border border-stone-300 px-3 py-3 text-base font-semibold text-stone-700">
                            Logout
                        </button>
                    </form>
                @else
                    <a href="{{ url('/login') }}" class="block rounded-lg bg-emerald-600 px-3 py-3 text-center text-base font-semibold text-white">Login</a>
                @endauth
            </div>
        </div>
    </div>
</header>

{{-- ===== FLASH MESSAGE ===== --}}
@if (session('status') || session('error'))
    <div class="mx-auto mt-4 w-full max-w-6xl px-4 sm:px-6">
        <div class="rounded-xl border px-4 py-3 text-sm font-medium
                    {{ session('error') ? 'border-red-200 bg-red-50 text-red-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700' }}">
            {{ session('error') ?? session('status') }}
        </div>
    </div>
@endif

{{-- ===== CONTENT ===== --}}
<main class="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6 sm:py-10">
    @yield('content')
</main>

{{-- ===== FOOTER ===== --}}
<footer class="safe-bottom border-t border-stone-200 bg-white">
    <div class="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-4 py-6 text-center text-sm text-stone-500 sm:flex-row sm:px-6 sm:text-left">
        <p><span class="font-semibold text-emerald-700">ZooLens</span> — Deteksi satwa interaktif &amp; edukasi kebun binatang berbasis AI.</p>
        <p>&copy; {{ date('Y') }} Kelompok 10 · Informatika, Universitas Kristen Petra</p>
    </div>
</footer>

<script>
    (function () {
        const btn = document.getElementById('navToggle');
        const menu = document.getElementById('mobileMenu');
        const iOpen = document.getElementById('iconOpen');
        const iClose = document.getElementById('iconClose');
        btn.addEventListener('click', function () {
            const open = menu.classList.toggle('hidden') === false;
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
            iOpen.classList.toggle('hidden', open);
            iClose.classList.toggle('hidden', !open);
        });
    })();
</script>
@stack('scripts')
</body>
</html>