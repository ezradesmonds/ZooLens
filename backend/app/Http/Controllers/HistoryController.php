<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class HistoryController extends Controller
{
    public function index(Request $request)
    {
        $histories = $request->user()
            ->detections()
            ->with('animal')
            ->latest()
            ->get()
            ->map(function ($detection) {
                $key = strtolower($detection->animal->common_name);

                return [
                    'animal' => $key,
                    'name' => config("zoolens.names_id.$key", $detection->animal->common_name),
                    'confidence' => (float) $detection->confidence,
                    'detected_at' => $detection->created_at->format('Y-m-d H:i:s'),
                    'fact' => $detection->animal->habitat === 'TODO' ? '' : $detection->animal->habitat,
                ];
            })
            ->all();

        return view('history', compact('histories'));
    }
}