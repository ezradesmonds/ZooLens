<?php

namespace App\Http\Controllers;

class HistoryController extends Controller
{
    /**
     * GET /history -> Halaman Riwayat Deteksi.
     * Data di bawah masih DUMMY. Ganti dengan query riwayat milik pengguna
     * (mis. Detection::where('user_id', auth()->id())->latest()->get()) setelah tabelnya siap.
     * Field yang dipakai view: animal, name, confidence (0..1), detected_at, fact, image_url (opsional).
     */
    public function index()
    {
        $histories = [
            ['animal' => 'zebra',    'name' => 'Zebra',   'confidence' => 0.94, 'detected_at' => '2026-10-15 09:41:00', 'fact' => 'Pola belang setiap zebra unik, seperti sidik jari manusia.'],
            ['animal' => 'giraffe',  'name' => 'Jerapah', 'confidence' => 0.88, 'detected_at' => '2026-10-13 14:05:00', 'fact' => 'Jerapah hanya tidur sekitar 30 menit hingga 2 jam per hari.'],
            ['animal' => 'elephant', 'name' => 'Gajah',   'confidence' => 0.91, 'detected_at' => '2026-10-12 10:24:00', 'fact' => 'Gajah adalah mamalia darat terbesar dan punya ingatan yang sangat kuat.'],
            ['animal' => 'elephant', 'name' => 'Gajah',   'confidence' => 0.73, 'detected_at' => '2026-10-12 10:19:00', 'fact' => 'Belalai gajah memiliki lebih dari 40.000 otot.'],
        ];

        return view('history', compact('histories'));
    }
}