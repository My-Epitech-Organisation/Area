plugins {
    // plugins are defined per-module; top-level is minimal here
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
