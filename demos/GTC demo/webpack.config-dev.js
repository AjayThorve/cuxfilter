const path = require("path");
const webpack = require("webpack");

// import config
const config = require('../../config.json')

module.exports = {
    entry: path.resolve(__dirname, "src/index.jsx"),
    devtool: "source-map",
    mode: "development",
    node: {
        fs: 'empty' // https://github.com/webpack-contrib/css-loader/issues/447 *shrug*
    },
    module: {
        rules: [{
                test: /\.(js|jsx)$/,
                exclude: /(node_modules)/,
                include: [path.resolve(__dirname)],
                loader: "babel-loader",
                options: { presets: ['env', 'react'] }
            },
            {
                test: /\.(css|scss)$/,
                use: [{
                    loader: "style-loader"
                }, {
                    loader: "css-loader",
                    options: {
                        sourceMap: true
                    }
                }, {
                    loader: "sass-loader",
                    options: {
                        sourceMap: true
                    }
                }]
            },
            {
                test: /\.(png|jpg|gif|svg)$/,
                use: [{
                    loader: "file-loader",
                    options: { name: "[path][name].[ext]" }
                }]
            }
        ]
    },
    resolve: {
        extensions: [".js", ".jsx", ".css", ".scss"]
    },
    output: {
        path: path.resolve(__dirname, "src"),
        publicPath: path.resolve(__dirname, "/"),
        filename: "bundle.js"
    },
    devServer: {
        contentBase: [path.join(__dirname, "src/"), path.resolve('../../')],
        port: config.gtc_demo_port_external,
        publicPath: "http://localhost:" + config.gtc_demo_port_external,
        hotOnly: true,
        open: false,

    },
    plugins: [new webpack.HotModuleReplacementPlugin()]
};