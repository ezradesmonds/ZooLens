@switch(strtolower($key ?? ''))
    @case('elephant')
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" class="{{ $class ?? 'h-16 w-16' }}" fill="none" aria-hidden="true">
            <circle cx="64" cy="64" r="60" fill="#EEF2FF" stroke="#C7D2FE" stroke-width="3"/>
            <path d="M40 44 C18 37, 15 74, 36 78 C43 79, 46 69, 45 57 Z" fill="#64748B"/>
            <path d="M38 49 C24 45, 22 69, 36 72 C40 73, 42 66, 41 57 Z" fill="#94A3B8"/>
            <path d="M88 44 C110 37, 113 74, 92 78 C85 79, 82 69, 83 57 Z" fill="#64748B"/>
            <path d="M90 49 C104 45, 106 69, 92 72 C88 73, 86 66, 87 57 Z" fill="#94A3B8"/>
            <path d="M39 54 C39 33, 89 33, 89 54 C89 72, 79 82, 64 82 C49 82, 39 72, 39 54 Z" fill="#475569"/>
            <path d="M48 73 Q40 85 49 91 Q52 84 53 75 Z" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>
            <path d="M80 73 Q88 85 79 91 Q76 84 75 75 Z" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>
            <path d="M56 69 C56 88, 56 105, 71 107 C80 108, 85 101, 83 95 C81 91, 76 92, 75 95 C74 98, 70 98, 69 94 C68 87, 70 78, 72 69 Z" fill="#475569"/>
            <path d="M60 79 Q64 81 68 79" stroke="#334155" stroke-width="2" stroke-linecap="round"/>
            <path d="M59 87 Q63 89 67 87" stroke="#334155" stroke-width="2" stroke-linecap="round"/>
            <path d="M60 95 Q64 97 67 95" stroke="#334155" stroke-width="2" stroke-linecap="round"/>
            <circle cx="51" cy="56" r="3.5" fill="#0F172A"/>
            <circle cx="52" cy="55" r="1.2" fill="#FFFFFF"/>
            <circle cx="77" cy="56" r="3.5" fill="#0F172A"/>
            <circle cx="78" cy="55" r="1.2" fill="#FFFFFF"/>
        </svg>
        @break

    @case('giraffe')
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" class="{{ $class ?? 'h-16 w-16' }}" fill="none" aria-hidden="true">
            <circle cx="64" cy="64" r="60" fill="#FEF3C7" stroke="#FDE68A" stroke-width="3"/>
            <path d="M52 65 L48 117 L80 117 L76 65 Z" fill="#F59E0B"/>
            <ellipse cx="58" cy="83" rx="4.5" ry="5.5" fill="#92400E"/>
            <ellipse cx="70" cy="91" rx="5" ry="4.5" fill="#92400E"/>
            <ellipse cx="57" cy="102" rx="5" ry="5.5" fill="#92400E"/>
            <ellipse cx="69" cy="110" rx="4.5" ry="4" fill="#92400E"/>
            <rect x="53" y="21" width="4" height="15" rx="2" fill="#92400E"/>
            <circle cx="55" cy="20" r="4.5" fill="#78350F"/>
            <rect x="71" y="21" width="4" height="15" rx="2" fill="#92400E"/>
            <circle cx="73" cy="20" r="4.5" fill="#78350F"/>
            <path d="M47 41 C33 36, 30 46, 44 49 Z" fill="#D97706"/>
            <path d="M81 41 C95 36, 98 46, 84 49 Z" fill="#D97706"/>
            <path d="M46 44 C46 32, 82 32, 82 44 L77 67 C75 74, 53 74, 51 67 Z" fill="#FBBF24"/>
            <circle cx="64" cy="40" r="3.5" fill="#B45309"/>
            <circle cx="57" cy="46" r="2.5" fill="#B45309"/>
            <circle cx="71" cy="46" r="2.5" fill="#B45309"/>
            <ellipse cx="64" cy="64" rx="13" ry="9" fill="#FDE68A"/>
            <circle cx="59" cy="63" r="2" fill="#78350F"/>
            <circle cx="69" cy="63" r="2" fill="#78350F"/>
            <path d="M60 68 Q64 71 68 68" stroke="#78350F" stroke-width="1.8" stroke-linecap="round"/>
            <circle cx="52" cy="50" r="3.3" fill="#1C1917"/>
            <circle cx="53" cy="49" r="1.1" fill="#FFFFFF"/>
            <circle cx="76" cy="50" r="3.3" fill="#1C1917"/>
            <circle cx="77" cy="49" r="1.1" fill="#FFFFFF"/>
        </svg>
        @break

    @case('zebra')
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" class="{{ $class ?? 'h-16 w-16' }}" fill="none" aria-hidden="true">
            <circle cx="64" cy="64" r="60" fill="#CCFBF1" stroke="#99F6E4" stroke-width="3"/>
            <path d="M56 32 L59 20 L63 30 L67 19 L71 30 L76 22 L76 34 Z" fill="#1E293B"/>
            <path d="M47 38 L41 21 L55 32 Z" fill="#FFFFFF" stroke="#334155" stroke-width="1.5" stroke-linejoin="round"/>
            <path d="M44 27 L41 21 L48 25 Z" fill="#1E293B"/>
            <path d="M81 38 L87 21 L73 32 Z" fill="#FFFFFF" stroke="#334155" stroke-width="1.5" stroke-linejoin="round"/>
            <path d="M84 27 L87 21 L80 25 Z" fill="#1E293B"/>
            <path d="M47 72 L43 116 L85 116 L81 72 Z" fill="#FFFFFF"/>
            <path d="M46 84 L60 88 L59 92 L45 89 Z" fill="#1E293B"/>
            <path d="M82 84 L68 88 L69 92 L83 89 Z" fill="#1E293B"/>
            <path d="M44 98 L61 102 L60 106 L44 103 Z" fill="#1E293B"/>
            <path d="M84 98 L67 102 L68 106 L84 103 Z" fill="#1E293B"/>
            <path d="M45 43 C45 29, 83 29, 83 43 L79 72 C77 82, 51 82, 49 72 Z" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
            <path d="M64 31 L56 40 L60 40 L64 35 L68 40 L72 40 Z" fill="#1E293B"/>
            <path d="M64 41 L58 49 L61 49 L64 44 L67 49 L70 49 Z" fill="#1E293B"/>
            <path d="M46 48 L56 51 L55 54 L46 52 Z" fill="#1E293B"/>
            <path d="M47 57 L57 59 L56 62 L48 61 Z" fill="#1E293B"/>
            <path d="M82 48 L72 51 L73 54 L82 52 Z" fill="#1E293B"/>
            <path d="M81 57 L71 59 L72 62 L80 61 Z" fill="#1E293B"/>
            <ellipse cx="64" cy="72" rx="14" ry="9.5" fill="#334155"/>
            <circle cx="59" cy="71" r="2.2" fill="#0F172A"/>
            <circle cx="69" cy="71" r="2.2" fill="#0F172A"/>
            <path d="M60 76 Q64 79 68 76" stroke="#0F172A" stroke-width="1.8" stroke-linecap="round"/>
            <circle cx="52" cy="46" r="3.3" fill="#0F172A"/>
            <circle cx="53" cy="45" r="1.1" fill="#FFFFFF"/>
            <circle cx="76" cy="46" r="3.3" fill="#0F172A"/>
            <circle cx="77" cy="45" r="1.1" fill="#FFFFFF"/>
        </svg>
        @break

    @case('tiger')
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" class="{{ $class ?? 'h-16 w-16' }}" fill="none" aria-hidden="true">
            <circle cx="64" cy="64" r="60" fill="#FFEDD5" stroke="#FED7AA" stroke-width="3"/>
            <circle cx="38" cy="39" r="12" fill="#EA580C"/>
            <circle cx="39" cy="40" r="6.5" fill="#FDBA74"/>
            <circle cx="90" cy="39" r="12" fill="#EA580C"/>
            <circle cx="89" cy="40" r="6.5" fill="#FDBA74"/>
            <path d="M31 62 C31 35, 97 35, 97 62 C97 86, 81 97, 64 97 C47 97, 31 86, 31 62 Z" fill="#F97316"/>
            <path d="M33 66 C33 84, 49 96, 64 96 C79 96, 95 84, 95 66 C84 68, 76 74, 64 74 C52 74, 44 68, 33 66 Z" fill="#FFF7ED"/>
            <rect x="62" y="38" width="4" height="13" rx="2" fill="#1C1917"/>
            <rect x="54" y="40" width="3.5" height="10" rx="1.7" fill="#1C1917"/>
            <rect x="70.5" y="40" width="3.5" height="10" rx="1.7" fill="#1C1917"/>
            <path d="M32 55 L46 57 L45 60.5 L32 59 Z" fill="#1C1917"/>
            <path d="M33 64 L47 65.5 L46 69 L34 68.5 Z" fill="#1C1917"/>
            <path d="M96 55 L82 57 L83 60.5 L96 59 Z" fill="#1C1917"/>
            <path d="M95 64 L81 65.5 L82 69 L94 68.5 Z" fill="#1C1917"/>
            <path d="M58 68 L70 68 L64 75 Z" fill="#BE123C"/>
            <path d="M64 75 L64 81 M64 81 Q58 85 54 81 M64 81 Q70 85 74 81" stroke="#1C1917" stroke-width="2.2" stroke-linecap="round"/>
            <circle cx="49" cy="57" r="3.8" fill="#1C1917"/>
            <circle cx="50.2" cy="55.8" r="1.3" fill="#FFFFFF"/>
            <circle cx="79" cy="57" r="3.8" fill="#1C1917"/>
            <circle cx="80.2" cy="55.8" r="1.3" fill="#FFFFFF"/>
        </svg>
        @break

    @case('rhinoceros')
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" class="{{ $class ?? 'h-16 w-16' }}" fill="none" aria-hidden="true">
            <circle cx="64" cy="64" r="60" fill="#F3E8FF" stroke="#E9D5FF" stroke-width="3"/>
            <path d="M40 48 L35 27 L50 42 Z" fill="#57534E"/>
            <path d="M49 45 L47 23 L60 40 Z" fill="#78716C"/>
            <path d="M75 51 C79 41, 84 35, 89 33 C90 40, 86 48, 82 54 Z" fill="#E2E8F0" stroke="#CBD5E1" stroke-width="1"/>
            <path d="M87 58 C93 41, 103 29, 110 25 C111 36, 105 50, 98 61 Z" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>
            <path d="M26 98 L33 54 C37 39, 58 35, 75 44 L96 56 C103 60, 103 74, 94 80 L76 86 L72 98 Z" fill="#78716C"/>
            <path d="M48 47 C45 62, 47 77, 54 92" stroke="#57534E" stroke-width="3" stroke-linecap="round"/>
            <path d="M68 51 C66 64, 68 74, 72 84" stroke="#57534E" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M81 78 Q91 78 97 74" stroke="#44403C" stroke-width="2.2" stroke-linecap="round"/>
            <circle cx="93" cy="68" r="2.3" fill="#44403C"/>
            <circle cx="61" cy="54" r="3.5" fill="#1C1917"/>
            <circle cx="62" cy="53" r="1.2" fill="#FFFFFF"/>
        </svg>
        @break
@endswitch