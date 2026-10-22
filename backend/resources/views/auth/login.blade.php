@extends('layouts.app')

@section('title', 'Login')

@section('content')
<div class="mx-auto grid max-w-5xl items-stretch overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-lg lg:grid-cols-2">

    {{-- Panel ilustrasi (desktop) --}}
    <aside class="relative hidden flex-col justify-between bg-gradient-to-br from-emerald-600 to-emerald-800 p-10 text-white lg:flex">
        <div>
            <p class="text-sm font-semibold uppercase tracking-wider text-emerald-100">Selamat datang kembali</p>
            <h2 class="mt-2 text-3xl font-extrabold leading-tight">Lanjutkan petualangan safari digitalmu</h2>
            <p class="mt-3 text-emerald-50">Masuk untuk menyimpan riwayat deteksi dan melanjutkan koleksi lencana satwamu.</p>
        </div>
        <div class="mt-8 flex gap-3 text-5xl" aria-hidden="true">
            <i class="fa-solid fa-paw opacity-100"></i><i class="fa-solid fa-paw opacity-90"></i><i class="fa-solid fa-paw opacity-80"></i><i class="fa-solid fa-paw opacity-70"></i><i class="fa-solid fa-paw opacity-60"></i>
        </div>
    </aside>

    {{-- Form --}}
    <section class="p-6 sm:p-10">
        <h1 class="text-2xl font-extrabold tracking-tight text-stone-900 sm:text-3xl">Masuk ke ZooLens</h1>
        <p class="mt-1 text-sm text-stone-500">Belum punya akun? <a href="{{ url('/register') }}" class="font-semibold text-emerald-700 hover:underline">Daftar sekarang</a></p>

        @if ($errors->any())
            <div class="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
                <p class="font-semibold">Login gagal</p>
                <ul class="mt-1 list-disc pl-5">
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        <form id="loginForm" method="POST" action="{{ url('/login') }}" class="mt-6 space-y-4" novalidate>
            @csrf

            <div>
                <label for="email" class="block text-sm font-semibold text-stone-700">Email</label>
                <input id="email" name="email" type="email" value="{{ old('email') }}" required autofocus autocomplete="email"
                       placeholder="nama@email.com"
                       class="mt-1 w-full rounded-xl border px-4 py-3 text-sm outline-none transition focus:ring-4
                              {{ $errors->has('email') ? 'border-red-400 focus:border-red-500 focus:ring-red-100' : 'border-stone-300 focus:border-emerald-500 focus:ring-emerald-100' }}">
                @error('email')<p class="mt-1 text-xs text-red-600">{{ $message }}</p>@enderror
            </div>

            <div>
                <div class="flex items-center justify-between">
                    <label for="password" class="block text-sm font-semibold text-stone-700">Password</label>
                </div>
                <div class="relative mt-1">
                    <input id="password" name="password" type="password" required autocomplete="current-password"
                           placeholder="Masukkan password"
                           class="w-full rounded-xl border px-4 py-3 pr-12 text-sm outline-none transition focus:ring-4
                                  {{ $errors->has('password') ? 'border-red-400 focus:border-red-500 focus:ring-red-100' : 'border-stone-300 focus:border-emerald-500 focus:ring-emerald-100' }}">
                    <button type="button" data-toggle-password="password" aria-label="Tampilkan password"
                            class="absolute inset-y-0 right-0 grid w-12 place-items-center text-stone-400 hover:text-stone-700"><i class="fa-solid fa-eye" aria-hidden="true"></i></button>
                </div>
                @error('password')<p class="mt-1 text-xs text-red-600">{{ $message }}</p>@enderror
            </div>

            <button id="submitBtn" type="submit"
                    class="w-full rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 active:scale-[.99] disabled:cursor-not-allowed disabled:opacity-60">
                Masuk
            </button>
        </form>
    </section>
</div>
@endsection

@push('scripts')
<script>
(function () {
    // Tampilkan / sembunyikan password
    document.querySelectorAll('[data-toggle-password]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var input = document.getElementById(btn.dataset.togglePassword);
            var show = input.type === 'password';
            input.type = show ? 'text' : 'password';
            btn.innerHTML = '<i class="fa-solid ' + (show ? 'fa-eye-slash' : 'fa-eye') + '" aria-hidden="true"></i>';
            btn.setAttribute('aria-label', show ? 'Sembunyikan password' : 'Tampilkan password');
        });
    });

    // Cegah submit ganda
    var form = document.getElementById('loginForm');
    var btn = document.getElementById('submitBtn');
    form.addEventListener('submit', function (e) {
        if (!form.email.value.trim() || !form.password.value) {
            e.preventDefault();
            (form.email.value.trim() ? form.password : form.email).focus();
            return;
        }
        btn.disabled = true;
        btn.textContent = 'Memproses…';
    });
})();
</script>
@endpush