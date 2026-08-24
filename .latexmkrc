$out_dir = 'build';
$pdf_mode = 1;
$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode %O %S';

# Create subdirectories for aux files from \include statements
use File::Path qw(make_path);
make_path("$out_dir/admin_chapters/committee_page",
          "$out_dir/admin_chapters/lay_summary",
          "$out_dir/admin_chapters/preface",
          "$out_dir/admin_chapters/acknowledgements",
          "$out_dir/admin_chapters/dedication",
          "$out_dir/body_chapters/introduction",
          "$out_dir/body_chapters/background",
          "$out_dir/body_chapters/related",
          "$out_dir/body_chapters/arch_structural",
          "$out_dir/body_chapters/arch_property",
          "$out_dir/body_chapters/eval_static",
          "$out_dir/body_chapters/eval_dynamic",
          "$out_dir/body_chapters/eval_property",
          "$out_dir/body_chapters/future_work",
          "$out_dir/body_chapters/conclusion",
          "$out_dir/body_chapters/appendix");
