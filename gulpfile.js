var concat = require('gulp-concat');
var gulp = require('gulp');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');

gulp.task('css', function() {
  return gulp.src([
      'assets/scss/main.scss',
      'assets/scss/badges.scss',
    ])
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        includePaths: 'node_modules',
      })
      .on('error', sass.logError)
    )
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest('static/css/'));
});

gulp.task('js', function() {
  return gulp.src([
      'node_modules/jquery/dist/jquery.js',
      'node_modules/popper.js/dist/umd/popper.js',
      'node_modules/bootstrap/dist/js/bootstrap.js',
      'node_modules/moment/moment.js',
      'node_modules/moment/locale/en-gb.js',
      'node_modules/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker.js',
      'node_modules/video.js/dist/video.js',
      'node_modules/video.js/dist/lang/en.js',
      'node_modules/videojs-contrib-hls/dist/videojs-contrib-hls.js',
      'node_modules/videojs-contrib-quality-levels/dist/videojs-contrib-quality-levels.js',
      'node_modules/videojs-hls-source-selector/dist/videojs-hls-source-selector.js',
      'assets/js/reg-form-dependency.js',
    ])
    .pipe(sourcemaps.init())
    .pipe(concat('debconf18.js'))
    .pipe(uglify())
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest('static/js'));
});

gulp.task('vendor-js', function() {
  return gulp.src('node_modules/jquery/dist/jquery.js')
    .pipe(sourcemaps.init())
    .pipe(uglify())
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest('static/js'));
});

gulp.task('assets', function() {
  return gulp.src('assets/{img,fonts,docs}/**/*')
    .pipe(gulp.dest('static/'));
});

gulp.task('font-awesome', function() {
  return gulp.src('node_modules/@fortawesome/fontawesome-free-webfonts/webfonts/*')
    .pipe(gulp.dest('static/fonts'));
});

gulp.task('videojs-font', function() {
    return gulp.src('node_modules/video.js/dist/font/*')
        .pipe(gulp.dest('static/css/font'));
});

gulp.task('watch', function() {
  gulp.watch('assets/js/*.js', ['js']);
  gulp.watch('assets/scss/*.scss', ['css']);
  gulp.watch('assets/img/*', ['assets']);
  gulp.watch('assets/fonts/*', ['assets']);
});

gulp.task('default', [
  'css',
  'js',
  'vendor-js',
  'assets',
  'font-awesome',
  'videojs-font',
]);
