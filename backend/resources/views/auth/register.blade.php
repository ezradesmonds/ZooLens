@extends('layouts.app')

@section('title', 'Daftar')

@section('content')
<div class="mx-auto grid max-w-5xl items-stretch overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-lg lg:grid-cols-2">

    {{-- Panel ilustrasi (desktop) --}}
    <aside class="relative hidden flex-col justify-between bg-gradient-to-br from-amber-500 to-orange-600 p-10 text-white lg:flex">
        <div>
            <p class="text-sm font-semibold uppercase tracking-wider text-amber-100">Bergabung dengan ZooLens</p>
            <h2 class="mt-2 text-3xl font-extrabold leading-tight">Kumpulkan semua lencana satwa</h2>
            <ul class="mt-4 space-y-2 text-amber-50">
                <li><i class="fa-solid fa-circle-check mr-2" aria-hidden="true"></i>Simpan riwayat deteksi satwa</li>
                <li><i class="fa-solid fa-circle-check mr-2" aria-hidden="true"></i>Buka lencana Zoo Digital Safari</li>
                <li><i class="fa-solid fa-circle-check mr-2" aria-hidden="true"></i>Pantau progres koleksimu</li>
            </ul>
        </div>
        <div class="mt-8 flex gap-3 text-5xl" aria-hidden="true">
            <i class="fa-solid fa-paw opacity-100"></i><i class="fa-solid fa-paw opacity-90"></i><i class="fa-solid fa-paw opacity-80"></i><i class="fa-solid fa-paw opacity-70"></i><i class="fa-solid fa-paw opacity-60"></i>
        </div>
    </aside>

    {{-- Form --}}
    <section class="p-6 sm:p-10">
        <h1 class="text-2xl font-extrabold tracking-tight text-stone-900 sm:text-3xl">Buat akun baru</h1>
        <p class="mt-1 text-sm text-stone-500">Sudah punya akun? <a href="{{ url('/login') }}" class="font-semibold text-emerald-700 hover:underline">Masuk</a></p>

        @if ($errors->any())
            <div class="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
                <p class="font-semibold">Pendaftaran belum berhasil</p>
                <ul class="mt-1 list-disc pl-5">
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        <form id="registerForm" method="POST" action="{{ url('/register') }}" class="mt-6 space-y-4" novalidate>
            @csrf

            <div>
                <label for="name" class="block text-sm font-semibold text-stone-700">Nama lengkap</label>
                <input id="name" name="name" type="text" value="{{ old('name') }}" required autofocus autocomplete="name"
                       placeholder="Nama kamu"
                       class="mt-1 w-full rounded-xl border px-4 py-3 text-sm outline-none transition focus:ring-4
                              {{ $errors->has('name') ? 'border-red-400 focus:border-red-500 focus:ring-red-100' : 'border-stone-300 focus:border-emerald-500 focus:ring-emerald-100' }}">
                @error('name')<p class="mt-1 text-xs text-red-600">{{ $message }}</p>@enderror
            </div>

            <div>
                <label for="email" class="block text-sm font-semibold text-stone-700">Email</label>
                <input id="email" name="email" type="email" value="{{ old('email') }}" required autocomplete="email"
                       placeholder="nama@email.com"
                       class="mt-1 w-full rounded-xl border px-4 py-3 text-sm outline-none transition focus:ring-4
                              {{ $errors->has('email') ? 'border-red-400 focus:border-red-500 focus:ring-red-100' : 'border-stone-300 focus:border-emerald-500 focus:ring-emerald-100' }}">
                @error('email')<p class="mt-1 text-xs text-red-600">{{ $message }}</p>@enderror
            </div>

            <div>
                <label for="password" class="block text-sm font-semibold text-stone-700">Password</label>
                <div class="relative mt-1">
                    <input id="password" name="password" type="password" required minlength="8" autocomplete="new-password"
                           placeholder="Minimal 8 karakter"
                           class="w-full rounded-xl border px-4 py-3 pr-12 text-sm outline-none transition focus:ring-4
                                  {{ $errors->has('password') ? 'border-red-400 focus:border-red-500 focus:ring-red-100' : 'border-stone-300 focus:border-emerald-500 focus:ring-emerald-100' }}">
                    <button type="button" data-toggle-password="password" aria-label="Tampilkan password"
                            class="absolute inset-y-0 right-0 grid w-12 place-items-center text-stone-400 hover:text-stone-700"><i class="fa-solid fa-eye" aria-hidden="true"></i></button>
                </div>
                {{-- Indikator kekuatan --}}
                <div class="mt-2 flex items-center gap-2">
                    <div class="grid flex-1 grid-cols-4 gap-1" aria-hidden="true">
                        <span class="strength-seg h-1.5 rounded-full bg-stone-200"></span>
                        <span class="strength-seg h-1.5 rounded-full bg-stone-200"></span>
                        <span class="strength-seg h-1.5 rounded-full bg-stone-200"></span>
                        <span class="strength-seg h-1.5 rounded-full bg-stone-200"></span>
                    </div>
                    <span id="strengthText" class="w-16 text-right text-xs font-semibold text-stone-400"></span>
                </div>
                @error('password')<p class="mt-1 text-xs text-red-600">{{ $message }}</p>@enderror
            </div>

            <div>
                <label for="password_confirmation" class="block text-sm font-semibold text-stone-700">Konfirmasi password</label>
                <div class="relative mt-1">
                    <input id="password_confirmation" name="password_confirmation" type="password" required autocomplete="new-password"
                           placeholder="Ulangi password"
                           class="w-full rounded-xl border border-stone-300 px-4 py-3 pr-12 text-sm outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100">
                    <button type="button" data-toggle-password="password_confirmation" aria-label="Tampilkan password"
                            class="absolute inset-y-0 right-0 grid w-12 place-items-center text-stone-400 hover:text-stone-700"><i class="fa-solid fa-eye" aria-hidden="true"></i></button>
                </div>
                <p id="matchMsg" class="mt-1 hidden text-xs"></p>
            </div>

            <button id="submitBtn" type="submit"
                    class="w-full rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 active:scale-[.99] disabled:cursor-not-allowed disabled:opacity-60">
                Daftar
            </button>
        </form>
    </section>
</div>
@endsection

@push('scripts')
<script>
(function () {
    var form = document.getElementById('registerForm');
    var pass = document.getElementById('password');
    var conf = document.getElementById('password_confirmation');
    var matchMsg = document.getElementById('matchMsg');
    var segs = document.querySelectorAll('.strength-seg');
    var strengthText = document.getElementById('strengthText');
    var btn = document.getElementById('submitBtn');

    // Tampilkan / sembunyikan password
    document.querySelectorAll('[data-toggle-password]').forEach(function (b) {
        b.addEventListener('click', function () {
            var input = document.getElementById(b.dataset.togglePassword);
            var show = input.type === 'password';
            input.type = show ? 'text' : 'password';
            b.innerHTML = '<i class="fa-solid ' + (show ? 'fa-eye-slash' : 'fa-eye') + '" aria-hidden="true"></i>';
            b.setAttribute('aria-label', show ? 'Sembunyikan password' : 'Tampilkan password');
        });
    });

    // Kekuatan password
    var levels = [
        { t: '',        c: 'bg-stone-200',  x: 'text-stone-400' },
        { t: 'Lemah',   c: 'bg-red-500',    x: 'text-red-500' },
        { t: 'Cukup',   c: 'bg-amber-500',  x: 'text-amber-600' },
        { t: 'Baik',    c: 'bg-lime-500',   x: 'text-lime-600' },
        { t: 'Kuat',    c: 'bg-emerald-500', x: 'text-emerald-600' },
    ];
    var allBg = ['bg-stone-200', 'bg-red-500', 'bg-amber-500', 'bg-lime-500', 'bg-emerald-500'];
    var allTx = ['text-stone-400', 'text-red-500', 'text-amber-600', 'text-lime-600', 'text-emerald-600'];

    function score(v) {
        if (!v) return 0;
        var s = 0;
        if (v.length >= 8) s++;
        if (/[a-z]/.test(v) && /[A-Z]/.test(v)) s++;
        if (/\d/.test(v)) s++;
        if (/[^A-Za-z0-9]/.test(v) || v.length >= 12) s++;
        return Math.max(1, s);
    }

    function updateStrength() {
        var lv = levels[pass.value ? score(pass.value) : 0];
        var n = pass.value ? score(pass.value) : 0;
        segs.forEach(function (seg, i) {
            seg.classList.remove.apply(seg.classList, allBg);
            seg.classList.add(i < n ? lv.c : 'bg-stone-200');
        });
        strengthText.classList.remove.apply(strengthText.classList, allTx);
        strengthText.classList.add(lv.x);
        strengthText.textContent = lv.t;
    }

    function updateMatch() {
        if (!conf.value) { matchMsg.classList.add('hidden'); return true; }
        var ok = pass.value === conf.value;
        matchMsg.classList.remove('hidden', 'text-red-600', 'text-emerald-600');
        matchMsg.classList.add(ok ? 'text-emerald-600' : 'text-red-600');
        matchMsg.innerHTML = ok ? '<i class="fa-solid fa-circle-check" aria-hidden="true"></i> Password cocok' : 'Password tidak sama';
        return ok;
    }

    pass.addEventListener('input', function () { updateStrength(); updateMatch(); });
    conf.addEventListener('input', updateMatch);

    form.addEventListener('submit', function (e) {
        var problem = null;
        if (!form.name.value.trim()) problem = form.name;
        else if (!form.email.value.trim()) problem = form.email;
        else if (pass.value.length < 8) problem = pass;
        else if (!updateMatch() || !conf.value) problem = conf;

        if (problem) { e.preventDefault(); problem.focus(); return; }
        btn.disabled = true;
        btn.textContent = 'Mendaftarkan…';
    });

    updateStrength();
})();
</script>
@endpush