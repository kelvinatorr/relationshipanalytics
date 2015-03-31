/**
 * Created by kelvin on 3/2/2015.
 */
module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        concat: {
            concatApp: {
                options: {
                    separator: ';'
                },
                files: [
                    {
                        //expand: true,     // Enable dynamic expansion.
                        //cwd: 'js/mysma/',      // Src matches are relative to this path.
                        src: ['js/app/**/*.js'], // Actual pattern(s) to match.
                        dest: 'build/js/app.concat.js'   // Destination path prefix.
                        //ext: '.huh.js'   // Dest filepaths will have this extension.
                    }
                ]
            }
        },
        uglify: {
            minifyJS: {
                options: {
                    banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
                },
                files: [
                    {
                        expand: true,     // Enable dynamic expansion.
                        cwd: 'js/app',      // Src matches are relative to this path.
                        src: ['**/*.js'], // Actual pattern(s) to match.
                        dest: 'build/js/',   // Destination path prefix.
                        ext: '.min.js',   // Dest filepaths will have this extension.
                        extDot: 'first'   // Extensions in filenames begin after the first dot
                    }
                ]
            },
            minifyApp : {
                options: {
                    banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
                },
                files: [
                    {

                        src: 'build/js/app.concat.js', // Actual pattern(s) to match.
                        dest: 'build/js/app.min.js'   // Destination path prefix.
                    }
                ]
            }
        }
        ,cssmin: {
            target: {
                files: [{
                    expand: true,
                    cwd: 'css/app',
                    src: ['*.css', '!*.min.css'],
                    dest: 'build/css',
                    ext: '.min.css'
                }]
            }
        }
    });

    // Load the plugin that provides the "uglify" task.
    grunt.loadNpmTasks('grunt-contrib-uglify');

    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-concat');

    // Default task(s).
    grunt.registerTask('default', ['concat:concatApp','uglify:minifyApp', 'cssmin']);

    grunt.registerTask('uglifyJs', ['uglify']);
    grunt.registerTask('minifyCss', ['cssmin']);
    grunt.registerTask('buildApp', ['concat:concatApp','uglify:minifyApp']);

};