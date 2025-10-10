import java.io.*;
import java.util.*;

public class Main {

    static class ENFA {
        Set<Character> states = new HashSet<>();
        Set<Character> alphabet = new HashSet<>();
        char startState;
        Set<Character> acceptingStates = new HashSet<>();
        Map<Character, Map<Character, Set<Character>>> transitions = new HashMap<>();

        public Set<Character> epsClosure(Set<Character> S) {
            Set<Character> closure = new HashSet<>(S);
            Stack<Character> stack = new Stack<>();
            stack.addAll(S);
            while (!stack.isEmpty()) {
                char q = stack.pop();
                Set<Character> epsMoves = transitions.getOrDefault(q, Collections.emptyMap())
                        .getOrDefault('ε', Collections.emptySet());
                for (char nxt : epsMoves) {
                    if (closure.add(nxt)) stack.push(nxt);
                }
            }
            return closure;
        }

        public Set<Character> move(Set<Character> S, char a) {
            Set<Character> result = new HashSet<>();
            for (char q : S) {
                result.addAll(transitions.getOrDefault(q, Collections.emptyMap())
                        .getOrDefault(a, Collections.emptySet()));
            }
            return result;
        }

        public NFA toNFA() {
            Map<Character, Map<Character, Set<Character>>> newDelta = new HashMap<>();
            Set<Character> newAccepts = new HashSet<>();
            for (char q : states) {
                Set<Character> qClosure = epsClosure(Set.of(q));
                if (!Collections.disjoint(qClosure, acceptingStates)) newAccepts.add(q);

                Map<Character, Set<Character>> row = new HashMap<>();
                for (char a : alphabet) {
                    Set<Character> dest = new HashSet<>();
                    for (char p : qClosure) {
                        dest.addAll(transitions.getOrDefault(p, Collections.emptyMap())
                                .getOrDefault(a, Collections.emptySet()));
                    }
                    Set<Character> finalDest = epsClosure(dest);
                    if (!finalDest.isEmpty()) row.put(a, finalDest);
                }
                newDelta.put(q, row);
            }
            return new NFA(states, alphabet, startState, newAccepts, newDelta);
        }

        public void printTransitionTable(String title) {
            System.out.println("\n" + title);
            int colWidth = 12;
            List<Character> alphList = new ArrayList<>(alphabet);
            Collections.sort(alphList);

            System.out.printf("%-" + colWidth + "s", "State");
            for (char a : alphList) System.out.printf("%-" + colWidth + "s", a);
            System.out.printf("%-" + colWidth + "s", "ε");
            System.out.println();

            List<Character> sortedStates = new ArrayList<>(states);
            Collections.sort(sortedStates);

            for (char state : sortedStates) {
                StringBuilder sb = new StringBuilder("   ");
                if (state == startState) sb.setCharAt(0, '→');
                if (acceptingStates.contains(state)) sb.setCharAt(1, '*');
                sb.append(state);
                System.out.printf("%-" + colWidth + "s", sb.toString());

                for (char a : alphList) {
                    Set<Character> next = transitions.getOrDefault(state, Collections.emptyMap())
                            .getOrDefault(a, Collections.emptySet());
                    System.out.printf("%-" + colWidth + "s", fmtSet(next));
                }

                Set<Character> epsNext = transitions.getOrDefault(state, Collections.emptyMap())
                        .getOrDefault('ε', Collections.emptySet());
                System.out.printf("%-" + colWidth + "s", fmtSet(epsNext));
                System.out.println();
            }
        }


        public void runWord(String word) {
            System.out.println("\nТрассировка слова: " + word);
            Set<Character> cur = epsClosure(Set.of(startState));
            System.out.printf("%-15s%-10s%-15s\n", "Current", "Symbol", "Next");

            for (int i = 0; i < word.length(); i++) {
                char ch = word.charAt(i);
                Set<Character> next = epsClosure(move(cur, ch));
                System.out.printf("%-15s%-10s%-15s\n", fmtSet(cur), ch, fmtSet(next));
                cur = next;
            }

            // Проверяем ε-переходы в конце
            cur = epsClosure(cur);
            System.out.printf("%-15s%-10s%-15s\n", fmtSet(cur), "ε", fmtSet(cur));
            boolean ok = !Collections.disjoint(cur, acceptingStates);
            System.out.println(ok ? "Слово принято" : "Слово отклонено");
        }

        private String fmtSet(Set<Character> s) {
            if (s.isEmpty()) return "-";
            List<Character> list = new ArrayList<>(s);
            Collections.sort(list);
            return list.toString();
        }
    }

    static class NFA {
        Set<Character> states;
        Set<Character> alphabet;
        char startState;
        Set<Character> acceptingStates;
        Map<Character, Map<Character, Set<Character>>> transitions;

        public NFA(Set<Character> states, Set<Character> alphabet, char startState, Set<Character> accepts,
                   Map<Character, Map<Character, Set<Character>>> transitions) {
            this.states = states;
            this.alphabet = alphabet;
            this.startState = startState;
            this.acceptingStates = accepts;
            this.transitions = transitions;
        }

        public void printTransitionTable(String title) {
            System.out.println("\n" + title);
            int colWidth = 15;
            List<Character> alphList = new ArrayList<>(alphabet);
            Collections.sort(alphList);

            System.out.printf("%-" + colWidth + "s", "State");
            for (char a : alphList) System.out.printf("%-" + colWidth + "s", a);
            System.out.println();

            List<Character> sortedStates = new ArrayList<>(states);
            Collections.sort(sortedStates);

            for (char state : sortedStates) {
                StringBuilder sb = new StringBuilder("   ");
                if (state == startState) sb.setCharAt(0, '→');
                if (acceptingStates.contains(state)) sb.setCharAt(1, '*');
                sb.append(state);
                System.out.printf("%-" + colWidth + "s", sb.toString());

                for (char a : alphList) {
                    Set<Character> next = transitions.getOrDefault(state, Collections.emptyMap())
                            .getOrDefault(a, Collections.emptySet());
                    System.out.printf("%-" + colWidth + "s", next.isEmpty() ? "-" : next.toString());
                }
                System.out.println();
            }
        }
    }

    public static ENFA readENFAFromCSV(String filename) throws IOException {
        ENFA nfa = new ENFA();
        BufferedReader br = new BufferedReader(new FileReader(filename));
        String line;

        // start
        line = br.readLine();
        nfa.startState = line.split(",")[1].charAt(0);

        // accept
        line = br.readLine();
        String[] parts = line.split(",");
        for (int i = 1; i < parts.length; i++) {
            if (!parts[i].isEmpty()) nfa.acceptingStates.add(parts[i].charAt(0));
        }

        // alphabet
        line = br.readLine();
        parts = line.split(",");
        List<Character> alphabetList = new ArrayList<>();
        for (String s : parts) {
            if (!s.isEmpty()) {
                char c = s.charAt(0);
                alphabetList.add(c);
                nfa.alphabet.add(c);
            }
        }


        // transitions
        while ((line = br.readLine()) != null) {
            if (line.trim().isEmpty()) continue;
            parts = line.split(",", -1);
            char state = parts[0].charAt(0);
            nfa.states.add(state);
            Map<Character, Set<Character>> map = new HashMap<>();

            // алфавитные переходы
            for (int i = 0; i < alphabetList.size(); i++) {
                if (i + 1 < parts.length && !parts[i + 1].isEmpty()) {
                    Set<Character> next = new HashSet<>();
                    for (char c : parts[i + 1].toCharArray()) next.add(c);
                    map.put(alphabetList.get(i), next);
                }
            }

            // ε-переход — последняя колонка
            if (parts.length > 1) {
                String epsCell = parts[parts.length - 1];
                if (!epsCell.isEmpty()) {
                    Set<Character> epsNext = new HashSet<>();
                    for (char c : epsCell.toCharArray()) epsNext.add(c);
                    map.put('ε', epsNext);
                }
            }

            nfa.transitions.put(state, map);
        }

        br.close();
        return nfa;
    }

    public static void main(String[] args) throws IOException {
        Scanner sc = new Scanner(System.in);
        System.out.print("Введите имя CSV-файла: ");
        String filename = sc.nextLine();

        ENFA enfa = readENFAFromCSV(filename);
        NFA nfa = enfa.toNFA();

        enfa.printTransitionTable("ε-NFA");
        nfa.printTransitionTable("NFA без ε-переходов");

        System.out.print("\nВведите слово для проверки: ");
        String word = sc.nextLine();

        System.out.println("\n--- ε-NFA ---");
        enfa.runWord(word);

        System.out.println("\n--- NFA без ε-переходов ---");
        runWordNFA(nfa, word);
    }

    public static void runWordNFA(NFA nfa, String word) {
        System.out.println("\nТрассировка слова: " + word);
        Set<Character> cur = Set.of(nfa.startState);
        System.out.printf("%-15s%-10s%-15s\n", "Current", "Symbol", "Next");

        for (int i = 0; i < word.length(); i++) {
            char ch = word.charAt(i);
            Set<Character> next = new HashSet<>();
            for (char q : cur) next.addAll(nfa.transitions.getOrDefault(q, Collections.emptyMap())
                    .getOrDefault(ch, Collections.emptySet()));
            System.out.printf("%-15s%-10s%-15s\n", fmtSet(cur), ch, fmtSet(next));
            cur = next;
        }

        boolean ok = !Collections.disjoint(cur, nfa.acceptingStates);
        System.out.printf("%-15s%-10s%-15s\n", fmtSet(cur), "-", fmtSet(cur));
        System.out.println(ok ? "Слово принято" : "Слово отклонено");
    }

    public static String fmtSet(Set<Character> s) {
        if (s.isEmpty()) return "-";
        List<Character> list = new ArrayList<>(s);
        Collections.sort(list);
        return list.toString();
    }
}
