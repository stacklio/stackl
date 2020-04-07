package helper_functions

### Helper function for checking if a key is present
has_key(x, k) { _ = x[k] }

pick_first(k, a, b) = a[k]
pick_first(k, a, b) = b[k] { not has_key(a, k) }

merge_objects(a, b) = c {
    ks := {k | some k; _ = a[k]} | {k | some k; _ = b[k]}
    c := {k: v | some k; ks[k]; v := pick_first(k, b, a)}
}

contains(colors, elem) {
  colors[_] = elem
}
