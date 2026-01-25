#!/usr/bin/env perl

use strict;
use warnings;
use File::stat;

my $HOME = $ENV{HOME};
my $base_dir = $HOME . "/" . "ZKillQueryData/queue";

my $previous_total = 0;

while (1) {
    my @json_files = glob ("$base_dir/*.json");
    my @zero_byte_files;
    my $total_files = scalar @json_files;

    foreach my $file (@json_files) {
        my $stat = stat($file);
        if ($stat && $stat->size == 0) {
            push @zero_byte_files, $file;
        }
    }

    my $zero_count = scalar @zero_byte_files;
    my $trend_info;
    
    if ($previous_total == 0) {
        $trend_info = "initial";
    } elsif ($total_files > $previous_total) {
        my $change = $total_files - $previous_total;
        $trend_info = "increased by $change";
    } elsif ($total_files < $previous_total) {
        my $change = $previous_total - $total_files;
        $trend_info = "decreased by $change";
    } else {
        $trend_info = "stable";
    }

    print "Queue Monitor: $total_files total files, $zero_count zero-byte files ($trend_info)\n";

    $previous_total = $total_files;
    sleep 60;
}



