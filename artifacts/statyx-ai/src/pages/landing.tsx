import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { BarChart3, Database, Wand2, LineChart, BrainCircuit, Network, FileText, ArrowRight, Shield, Zap } from "lucide-react";

export default function Landing() {
  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  const stagger = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans selection:bg-primary/20 selection:text-primary">
      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 md:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-semibold text-lg tracking-tight">
            <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center text-primary-foreground shadow-sm">
              <BarChart3 size={18} />
            </div>
            Statyx AI
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost" className="text-muted-foreground hover:text-foreground">Log in</Button>
            </Link>
            <Link href="/register">
              <Button className="shadow-sm">Start Analyzing</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-24 md:py-32 lg:py-40 relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-background to-background -z-10" />
          <div className="container mx-auto px-4 md:px-6">
            <motion.div 
              initial="hidden"
              animate="visible"
              variants={stagger}
              className="max-w-4xl mx-auto text-center space-y-8"
            >
              <motion.div variants={fadeIn} className="inline-flex items-center rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-sm text-primary font-medium">
                <span className="flex h-2 w-2 rounded-full bg-primary mr-2"></span>
                The new standard for data research
              </motion.div>
              <motion.h1 variants={fadeIn} className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-foreground">
                Analyze data with <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-chart-2">absolute clarity.</span>
              </motion.h1>
              <motion.p variants={fadeIn} className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                Statyx AI is a precision instrument for serious researchers. Clean, visualize, and extract AI-driven insights from your datasets in a focused, clutter-free environment.
              </motion.p>
              <motion.div variants={fadeIn} className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
                <Link href="/register">
                  <Button size="lg" className="w-full sm:w-auto text-base h-12 px-8 shadow-sm">
                    Open Workspace <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="#features">
                  <Button variant="outline" size="lg" className="w-full sm:w-auto text-base h-12 px-8">
                    Explore Features
                  </Button>
                </Link>
              </motion.div>
            </motion.div>

            {/* Dashboard Mockup */}
            <motion.div 
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.8, ease: "easeOut" }}
              className="mt-20 mx-auto max-w-5xl rounded-xl border border-border/50 bg-card/50 shadow-2xl overflow-hidden backdrop-blur-sm"
            >
              <div className="h-8 border-b border-border/50 bg-muted/50 flex items-center px-4 gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-destructive/80"></div>
                  <div className="w-3 h-3 rounded-full bg-chart-4/80"></div>
                  <div className="w-3 h-3 rounded-full bg-chart-3/80"></div>
                </div>
              </div>
              <div className="aspect-[16/9] bg-card p-2 md:p-8 flex items-center justify-center text-muted-foreground relative">
                 {/* Abstract representation of the dashboard */}
                 <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
                 <div className="z-10 grid grid-cols-1 md:grid-cols-3 gap-6 w-full h-full max-w-4xl">
                    <div className="col-span-1 md:col-span-2 space-y-6">
                      <div className="h-32 bg-primary/5 rounded-lg border border-primary/10 flex items-end p-4">
                        <div className="w-full h-1/2 bg-primary/20 rounded-md"></div>
                      </div>
                      <div className="flex gap-6 h-48">
                         <div className="flex-1 bg-chart-2/5 rounded-lg border border-chart-2/10"></div>
                         <div className="flex-1 bg-chart-3/5 rounded-lg border border-chart-3/10"></div>
                      </div>
                    </div>
                    <div className="space-y-6">
                      <div className="h-24 bg-card shadow-sm border border-border rounded-lg"></div>
                      <div className="h-24 bg-card shadow-sm border border-border rounded-lg"></div>
                      <div className="h-24 bg-card shadow-sm border border-border rounded-lg"></div>
                    </div>
                 </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 bg-muted/30">
          <div className="container mx-auto px-4 md:px-6">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">A complete research lifecycle</h2>
              <p className="text-lg text-muted-foreground">From raw CSVs to publish-ready reports in one seamless workflow.</p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {[
                { icon: Database, title: "Data Ingestion", desc: "Upload massive datasets securely. We handle the parsing, typing, and initial profiling instantly." },
                { icon: Wand2, title: "Automated Cleaning", desc: "Handle missing values, outliers, and normalization with precision tools built for accuracy." },
                { icon: BarChart3, title: "Descriptive Stats", desc: "Generate comprehensive statistical summaries with one click, perfectly formatted for academic review." },
                { icon: LineChart, title: "Rich Visualizations", desc: "Create interactive, high-fidelity charts that reveal the hidden patterns in your data." },
                { icon: BrainCircuit, title: "AI Analysis", desc: "Apply advanced machine learning algorithms without writing a single line of Python." },
                { icon: Network, title: "Cross Tabulation", desc: "Discover complex relationships between variables with multi-dimensional contingency tables." }
              ].map((feature, i) => (
                <div key={i} className="group relative bg-card p-8 rounded-xl border border-border/50 shadow-sm hover:shadow-md transition-all">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center text-primary mb-6 group-hover:scale-110 transition-transform">
                    <feature.icon size={24} />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Trust Section */}
        <section className="py-24 border-y border-border/40">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid md:grid-cols-2 gap-12 items-center max-w-5xl mx-auto">
              <div className="space-y-6">
                <h2 className="text-3xl md:text-4xl font-bold tracking-tight">Built for rigor. Designed for speed.</h2>
                <p className="text-lg text-muted-foreground">We understand that your research reputation depends on data accuracy. Statyx AI doesn't cut corners—it accelerates the tedious parts so you can focus on the insights.</p>
                <ul className="space-y-4 pt-4">
                  {[
                    { icon: Shield, text: "Bank-grade data security and encryption" },
                    { icon: Zap, text: "Lightning-fast processing via Streamlit engine" },
                    { icon: FileText, text: "Export-ready, reproducible reporting" }
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-3 text-foreground font-medium">
                      <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-primary">
                        <item.icon size={16} />
                      </div>
                      {item.text}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 to-chart-2/10 rounded-2xl blur-3xl -z-10"></div>
                <div className="bg-card border border-border p-8 rounded-2xl shadow-lg relative z-0">
                  <div className="space-y-6">
                    <div className="flex items-center gap-4 border-b border-border pb-4">
                      <div className="w-12 h-12 rounded-full bg-muted"></div>
                      <div>
                        <div className="h-4 w-32 bg-muted rounded mb-2"></div>
                        <div className="h-3 w-24 bg-muted/60 rounded"></div>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="h-3 w-full bg-muted rounded"></div>
                      <div className="h-3 w-5/6 bg-muted rounded"></div>
                      <div className="h-3 w-4/6 bg-muted rounded"></div>
                    </div>
                    <div className="pt-4 flex gap-2">
                      <div className="h-8 w-20 bg-primary/10 rounded-md"></div>
                      <div className="h-8 w-20 bg-chart-2/10 rounded-md"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 relative overflow-hidden">
          <div className="absolute inset-0 bg-primary/5 -z-10" />
          <div className="container mx-auto px-4 md:px-6 text-center max-w-3xl">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6">Ready to elevate your research?</h2>
            <p className="text-xl text-muted-foreground mb-10">Join the researchers who use Statyx AI to process, analyze, and publish with confidence.</p>
            <Link href="/register">
              <Button size="lg" className="text-lg h-14 px-10 shadow-md">
                Create your workspace
              </Button>
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="container mx-auto px-4 md:px-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2 font-semibold text-lg">
            <BarChart3 size={20} className="text-primary" />
            Statyx AI
          </div>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
            <a href="#" className="hover:text-foreground transition-colors">Terms</a>
            <a href="#" className="hover:text-foreground transition-colors">Documentation</a>
            <a href="#" className="hover:text-foreground transition-colors">Support</a>
          </div>
          <p className="text-sm text-muted-foreground">© 2025 Statyx AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
