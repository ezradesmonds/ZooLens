<?php

namespace App\Http\Controllers;

class SafariController extends Controller
{
    /**
     * GET /safari -> Halaman Zoo Digital Safari (koleksi lencana).
     * Data di bawah masih DUMMY. Ganti dengan query ke tabel progres koleksi pengguna
     * setelah database siap (field yang dipakai view: key, name, en, unlocked, unlocked_at).
     */
    public function index()
    {
        $animals = [
            ['key' => 'elephant',   'name' => 'Gajah',   'en' => 'Elephant',   'unlocked' => true,  'unlocked_at' => '2026-10-12 10:24:00'],
            ['key' => 'giraffe',    'name' => 'Jerapah', 'en' => 'Giraffe',    'unlocked' => true,  'unlocked_at' => '2026-10-13 14:05:00'],
            ['key' => 'zebra',      'name' => 'Zebra',   'en' => 'Zebra',      'unlocked' => true,  'unlocked_at' => '2026-10-15 09:41:00'],
            ['key' => 'tiger',      'name' => 'Harimau', 'en' => 'Tiger',      'unlocked' => false, 'unlocked_at' => null],
            ['key' => 'rhinoceros', 'name' => 'Badak',   'en' => 'Rhinoceros', 'unlocked' => false, 'unlocked_at' => null],
        ];

        $total    = count($animals);
        $unlocked = count(array_filter($animals, fn ($a) => $a['unlocked']));
        $percent  = $total > 0 ? (int) round($unlocked / $total * 100) : 0;

        $dataDummy = [
            'animals'  => $animals,
            'total'    => $total,
            'unlocked' => $unlocked,
            'percent'  => $percent,
        ];

        return view('safari', $dataDummy);
    }
}