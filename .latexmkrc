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
          "$out_dir/body_chapters");
