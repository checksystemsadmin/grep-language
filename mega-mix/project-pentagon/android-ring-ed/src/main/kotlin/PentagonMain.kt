package pentagon

import java.io.File

object PentagonMain {
    @JvmStatic
    fun main(args: Array<String>) {
        if (args.size != 2 || args[0] != "--native") {
            System.err.println("Usage: java -jar pentagon.jar --native <absolute-native-executable>")
            kotlin.system.exitProcess(2)
        }
        val executable = File(args[1]).canonicalFile
        val runtime = File(System.getenv("PENTAGON_RUNTIME_DIR") ?: "./runtime").canonicalFile
        PentagonOrchestrator(executable, runtime).use { supervisor ->
            supervisor.start().getOrElse {
                System.err.println("Project Pentagon startup failed: ${it.message}")
                kotlin.system.exitProcess(1)
            }
            Runtime.getRuntime().addShutdownHook(Thread { supervisor.close() })
            while (true) {
                val result = supervisor.sampleBattery()
                println("PENTAGON_STATUS=${result.state}")
                if (result.requestShutdown) break
                Thread.sleep(15_000)
            }
        }
    }
}
