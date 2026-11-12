<?php

namespace App\Http\Controllers;

use App\Models\Animal;
use Illuminate\Http\Request;

class SafariController extends Controller
{
    public function index(Request $request)
    {
        $found = $request->user()->animals()->get()->keyBy('id');

        $animals = Animal::orderBy('class_id')->get()->map(function (Animal $animal) use ($found) {
            $key = strtolower($animal->common_name);
            $hit = $found->get($animal->id);

            return [
                'key' => $key,
                'name' => config("zoolens.names_id.$key", $animal->common_name),
                'en' => $animal->common_name,
                'unlocked' => $hit !== null,
                'unlocked_at' => $hit?->pivot->discovered_at,
            ];
        })->all();

        $total = count($animals);
        $unlocked = count(array_filter($animals, fn ($a) => $a['unlocked']));
        $percent = $total > 0 ? (int) round($unlocked / $total * 100) : 0;

        return view('safari', [
            'animals' => $animals,
            'total' => $total,
            'unlocked' => $unlocked,
            'percent' => $percent,
        ]);
    }
}