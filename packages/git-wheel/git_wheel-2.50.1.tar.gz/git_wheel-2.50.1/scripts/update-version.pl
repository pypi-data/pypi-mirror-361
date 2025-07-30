#!/usr/bin/env -S perl -pi
BEGIN {
    exit if scalar @ARGV == 0;
    $version =
`curl -s https://api.github.com/repos/git-for-windows/git/releases/latest | jq -r .tag_name`;
    chomp $version;
    $version =~ s/^v//;
    $version =~ s/\.windows\.\d+$//;
}

s/(?<=version = ")[^"]+/$version/;
