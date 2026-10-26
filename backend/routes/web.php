<?php
use App\Http\Controllers\AuthController;
use App\Http\Controllers\HistoryController;
use App\Http\Controllers\SafariController;
use App\Http\Controllers\ScanController;
use App\Http\Controllers\ScannerController;
use Illuminate\Support\Facades\Route;

Route::middleware('guest')->group(function () {
    Route::get('/register', [AuthController::class, 'showRegister'])->name('register');
    Route::post('/register', [AuthController::class, 'register']);
    Route::get('/login', [AuthController::class, 'showLogin'])->name('login');
    Route::post('/login', [AuthController::class, 'login']);
});

Route::middleware('auth')->group(function () {
    Route::post('/logout', [AuthController::class, 'logout'])->name('logout');

    Route::get('/', [ScannerController::class, 'index'])->name('scanner');
    Route::post('/scan', [ScanController::class, 'store'])->name('scan');
    Route::get('/safari', [SafariController::class, 'index'])->name('safari');
    Route::get('/history', [HistoryController::class, 'index'])->name('history');
});
